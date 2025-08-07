"""
Security utilities for contact form spam prevention and rate limiting.
"""

import re
import hashlib
from datetime import datetime, timedelta
from flask import request, current_app
from app.models import ContactSubmissionLog, ContactMessage, db
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Common spam keywords and patterns
SPAM_KEYWORDS = [
    'bitcoin', 'cryptocurrency', 'investment', 'trading', 'forex', 'casino',
    'viagra', 'cialis', 'pharmacy', 'pills', 'weight loss', 'diet pills',
    'make money', 'earn money', 'work from home', 'business opportunity',
    'guaranteed', 'no risk', 'limited time', 'act now', 'urgent',
    'click here', 'visit our website', 'check out our', 'amazing deal',
    'seo services', 'backlinks', 'increase traffic', 'ranking',
    'loan', 'credit', 'debt', 'mortgage', 'insurance',
    'replica', 'fake', 'counterfeit', 'cheap', 'discount'
]

# Suspicious patterns
SPAM_PATTERNS = [
    r'https?://[^\s]+',  # Multiple URLs
    r'\b[A-Z]{3,}\b',    # Excessive caps
    r'[!]{2,}',          # Multiple exclamation marks
    r'\$\d+',            # Dollar amounts
    r'\b\d{10,}\b',      # Long numbers (phone/spam)
    r'[^\w\s]{3,}',      # Special character sequences
]

def get_client_ip() -> str:
    """Get the real client IP address, accounting for proxies."""
    # Check for forwarded IP first (common with reverse proxies)
    forwarded_ips = request.headers.get('X-Forwarded-For')
    if forwarded_ips:
        # Take the first IP in the chain (original client)
        return forwarded_ips.split(',')[0].strip()
    
    # Check other common proxy headers
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct connection IP
    return request.remote_addr or '127.0.0.1'

def get_client_fingerprint() -> str:
    """Generate a fingerprint for the client based on IP and User-Agent."""
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', '')
    
    # Create a hash of IP + User-Agent for fingerprinting
    fingerprint_data = f"{ip}:{user_agent}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

def check_rate_limit(ip_address: str, email: str = None) -> Tuple[bool, Dict[str, any]]:
    """
    Check if the client is rate limited.
    
    Returns:
        Tuple of (is_allowed, rate_limit_info)
    """
    now = datetime.utcnow()
    
    # Define rate limits
    LIMITS = {
        'per_minute': {'count': 2, 'window': timedelta(minutes=1)},
        'per_hour': {'count': 10, 'window': timedelta(hours=1)},
        'per_day': {'count': 50, 'window': timedelta(days=1)}
    }
    
    rate_limit_info = {
        'remaining': {},
        'reset_times': {},
        'blocked_until': None
    }
    
    for limit_name, limit_config in LIMITS.items():
        window_start = now - limit_config['window']
        
        # Count submissions in this window
        query = ContactSubmissionLog.query.filter(
            ContactSubmissionLog.ip_address == ip_address,
            ContactSubmissionLog.submitted_at >= window_start
        )
        
        if email:
            # Also check by email for additional protection
            query = query.union(
                ContactSubmissionLog.query.filter(
                    ContactSubmissionLog.email == email,
                    ContactSubmissionLog.submitted_at >= window_start
                )
            )
        
        submission_count = query.count()
        
        rate_limit_info['remaining'][limit_name] = max(0, limit_config['count'] - submission_count)
        rate_limit_info['reset_times'][limit_name] = now + limit_config['window']
        
        if submission_count >= limit_config['count']:
            rate_limit_info['blocked_until'] = now + limit_config['window']
            logger.warning(f"Rate limit exceeded for IP {ip_address}: {submission_count} submissions in {limit_name}")
            return False, rate_limit_info
    
    return True, rate_limit_info

def calculate_spam_score(name: str, email: str, subject: str, message: str) -> float:
    """
    Calculate a spam score for the message content.
    
    Returns:
        Float between 0.0 (not spam) and 1.0 (definitely spam)
    """
    score = 0.0
    factors = []
    
    # Combine all text for analysis
    all_text = f"{name} {email} {subject} {message}".lower()
    
    # Check for spam keywords
    keyword_matches = sum(1 for keyword in SPAM_KEYWORDS if keyword in all_text)
    if keyword_matches > 0:
        keyword_score = min(keyword_matches * 0.1, 0.4)
        score += keyword_score
        factors.append(f"spam_keywords: {keyword_matches} matches (+{keyword_score:.2f})")
    
    # Check for spam patterns
    pattern_matches = 0
    for pattern in SPAM_PATTERNS:
        matches = len(re.findall(pattern, all_text))
        pattern_matches += matches
    
    if pattern_matches > 0:
        pattern_score = min(pattern_matches * 0.05, 0.3)
        score += pattern_score
        factors.append(f"spam_patterns: {pattern_matches} matches (+{pattern_score:.2f})")
    
    # Check message length (very short or very long can be suspicious)
    message_len = len(message.strip())
    if message_len < 10:
        score += 0.2
        factors.append("very_short_message (+0.2)")
    elif message_len > 2000:
        score += 0.15
        factors.append("very_long_message (+0.15)")
    
    # Check for suspicious email patterns
    if re.search(r'\d{5,}', email):  # Many numbers in email
        score += 0.1
        factors.append("numeric_email (+0.1)")
    
    # Check for repeated characters
    if re.search(r'(.)\1{4,}', all_text):  # 5+ repeated characters
        score += 0.1
        factors.append("repeated_chars (+0.1)")
    
    # Check for no spaces in message (bot-like)
    if ' ' not in message.strip():
        score += 0.2
        factors.append("no_spaces (+0.2)")
    
    # Check for excessive punctuation
    punct_ratio = len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', message)) / max(len(message), 1)
    if punct_ratio > 0.1:
        punct_score = min(punct_ratio * 0.5, 0.2)
        score += punct_score
        factors.append(f"excessive_punct: {punct_ratio:.2f} ratio (+{punct_score:.2f})")
    
    # Log spam analysis for debugging
    if score > 0.1:
        logger.info(f"Spam analysis for {email}: score={score:.3f}, factors={factors}")
    
    return min(score, 1.0)

def is_suspicious_user_agent(user_agent: str) -> bool:
    """Check if the user agent looks suspicious."""
    if not user_agent:
        return True
    
    user_agent_lower = user_agent.lower()
    
    # Known bot patterns
    bot_patterns = [
        'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python',
        'requests', 'urllib', 'http', 'java', 'go-http', 'okhttp'
    ]
    
    return any(pattern in user_agent_lower for pattern in bot_patterns)

def log_submission_attempt(ip_address: str, email: str, success: bool = True) -> None:
    """Log a contact form submission attempt."""
    try:
        log_entry = ContactSubmissionLog(
            ip_address=ip_address,
            email=email,
            success=success,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log_entry)
        db.session.commit()
        
        logger.info(f"Logged contact submission: IP={ip_address}, email={email}, success={success}")
    except Exception as e:
        logger.error(f"Failed to log submission attempt: {e}")
        db.session.rollback()

def cleanup_old_logs(days_to_keep: int = 30) -> None:
    """Clean up old submission logs to prevent database bloat."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted = ContactSubmissionLog.query.filter(
            ContactSubmissionLog.submitted_at < cutoff_date
        ).delete()
        
        db.session.commit()
        logger.info(f"Cleaned up {deleted} old submission logs")
    except Exception as e:
        logger.error(f"Failed to clean up old logs: {e}")
        db.session.rollback()

def is_honeypot_triggered(form_data: dict) -> bool:
    """
    Check if honeypot fields are filled (indicating bot submission).
    This function expects honeypot fields to be added to the form.
    """
    # Common honeypot field names that bots might fill
    honeypot_fields = ['website', 'url', 'phone_number', 'fax', 'company']
    
    for field in honeypot_fields:
        if field in form_data and form_data[field].strip():
            logger.warning(f"Honeypot triggered: field '{field}' was filled")
            return True
    
    return False

def validate_recaptcha_freshness(session_data: dict) -> bool:
    """
    Ensure reCAPTCHA validation is fresh and hasn't been reused.
    """
    last_recaptcha = session_data.get('last_recaptcha_validation')
    if not last_recaptcha:
        return False
    
    # reCAPTCHA should be validated within the last 5 minutes
    if datetime.utcnow() - datetime.fromisoformat(last_recaptcha) > timedelta(minutes=5):
        logger.warning("reCAPTCHA validation is stale")
        return False
    
    return True