"""
Main blueprint routes for the hacker terminal personal brand page.
"""

from flask import render_template, request, flash, redirect, url_for, current_app, session
from app.blueprints.main import bp
from app.models import BlogPost, PortfolioItem, ContactMessage
from app.forms import ContactForm
try:
    from app.forms import ContactFormWithRecaptcha
    RECAPTCHA_FORM_AVAILABLE = True
except ImportError:
    RECAPTCHA_FORM_AVAILABLE = False
    ContactFormWithRecaptcha = None
from app import db
from app.github_stats import github_stats
from app.email_utils import send_contact_form_email, send_contact_confirmation_email

# Import SEO routes to register them
from app.blueprints.main import seo_routes

@bp.route('/')
@bp.route('/index')
def index():
    """Homepage with terminal interface."""
    # Get latest blog posts
    latest_posts = BlogPost.query.filter_by(is_published=True)\
                                 .order_by(BlogPost.published_at.desc())\
                                 .limit(3).all()
    
    # Get featured portfolio items
    portfolio_items = PortfolioItem.query.filter_by(is_featured=True)\
                                        .order_by(PortfolioItem.sort_order)\
                                        .all()
    
    # If no featured items, get all items
    if not portfolio_items:
        portfolio_items = PortfolioItem.query.order_by(PortfolioItem.sort_order).all()
    
 
    
    return render_template('main/index.html', 
                         latest_posts=latest_posts,
                         portfolio_items=portfolio_items)

@bp.route('/portfolio')
@bp.route('/portfolio/')
def portfolio():
    """Portfolio showcase page."""
    items = PortfolioItem.query.order_by(PortfolioItem.sort_order).all()
    return render_template('main/portfolio.html', portfolio_items=items)

@bp.route('/about')
@bp.route('/about/')
def about():
    """About page with personal information."""
    return render_template('main/about.html')

@bp.route('/contact', methods=['GET', 'POST'])
@bp.route('/contact/', methods=['GET', 'POST'])
def contact():
    """Contact form page with comprehensive spam protection."""
    from app.security_utils import (
        get_client_ip, check_rate_limit, calculate_spam_score,
        is_suspicious_user_agent, log_submission_attempt, is_honeypot_triggered
    )
    from datetime import datetime
    
    # Use reCAPTCHA form if available and configured
    use_recaptcha = (RECAPTCHA_FORM_AVAILABLE and 
                    current_app.config.get('RECAPTCHA_PUBLIC_KEY') and 
                    current_app.config.get('RECAPTCHA_PRIVATE_KEY'))
    
    if use_recaptcha:
        form = ContactFormWithRecaptcha()
    else:
        form = ContactForm()
    
    if form.validate_on_submit():
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        
        # Security checks
        security_failed = False
        failure_reason = None
        
        # 1. Rate limiting check
        is_allowed, rate_info = check_rate_limit(client_ip, form.email.data)
        if not is_allowed:
            security_failed = True
            failure_reason = "rate_limit_exceeded"
            current_app.logger.warning(f"Rate limit exceeded for IP {client_ip}")
            flash('Too many requests. Please wait before submitting another message.', 'error')
        
        # 2. Honeypot check
        elif is_honeypot_triggered(request.form.to_dict()):
            security_failed = True
            failure_reason = "honeypot_triggered"
            current_app.logger.warning(f"Honeypot triggered for IP {client_ip}")
            # Don't show error message to bot - just silently fail
            flash('Message sent successfully! I\'ll get back to you soon.', 'success')
        
        # 3. Suspicious User-Agent check
        elif is_suspicious_user_agent(user_agent):
            security_failed = True
            failure_reason = "suspicious_user_agent"
            current_app.logger.warning(f"Suspicious user agent from IP {client_ip}: {user_agent}")
            flash('Your browser appears to be automated. Please use a standard web browser.', 'error')
        
        # 4. reCAPTCHA freshness check (if enabled)
        elif use_recaptcha and 'last_recaptcha_validation' in session:
            last_validation = session.get('last_recaptcha_validation')
            if last_validation:
                try:
                    last_time = datetime.fromisoformat(last_validation)
                    if (datetime.utcnow() - last_time).total_seconds() < 2:
                        security_failed = True
                        failure_reason = "recaptcha_too_fast"
                        current_app.logger.warning(f"reCAPTCHA solved too quickly by IP {client_ip}")
                        flash('Please wait a moment before submitting.', 'error')
                except:
                    pass
        
        # Log the submission attempt
        log_submission_attempt(client_ip, form.email.data, success=not security_failed)
        
        if security_failed:
            # Mark reCAPTCHA as used to prevent reuse
            if 'last_recaptcha_validation' in session:
                del session['last_recaptcha_validation']
            return redirect(url_for('main.contact'))
        
        # Calculate spam score
        spam_score = calculate_spam_score(
            form.name.data, 
            form.email.data, 
            form.subject.data or '', 
            form.message.data
        )
        
        # Create new contact message with security data
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
            ip_address=client_ip,
            user_agent=user_agent[:500],  # Truncate to fit database
            spam_score=spam_score,
            is_spam=(spam_score > 0.7)  # Mark as spam if score is high
        )
        
        db.session.add(message)
        
        try:
            # Only send emails for non-spam messages
            email_sent = False
            confirmation_sent = False
            
            if not message.is_spam:
                # Send email notification
                email_sent = send_contact_form_email(
                    name=form.name.data,
                    email=form.email.data,
                    subject=form.subject.data,
                    message=form.message.data
                )
                
                # Send confirmation email to user
                confirmation_sent = send_contact_confirmation_email(
                    name=form.name.data,
                    email=form.email.data
                )
            else:
                current_app.logger.warning(f"Spam message detected (score: {spam_score:.3f}) from {client_ip}")
            
            db.session.commit()
            
            # Mark reCAPTCHA as used
            if 'last_recaptcha_validation' in session:
                del session['last_recaptcha_validation']
            
            # Update session timestamp to prevent rapid resubmission
            session['last_submission'] = datetime.utcnow().isoformat()
            
            if message.is_spam:
                # Show success message to potential spammer to avoid revealing detection
                flash('Message sent successfully! I\'ll get back to you soon.', 'success')
            elif email_sent:
                flash('Message sent successfully! I\'ll get back to you soon.', 'success')
            else:
                flash('Message saved but email notification failed. I\'ll still see your message and respond soon.', 'warning')
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Contact form error: {str(e)}")
            flash('There was an error sending your message. Please try again or contact me directly.', 'error')
            
        return redirect(url_for('main.contact'))
    
    # For GET requests, mark reCAPTCHA validation timestamp if form was just loaded
    if request.method == 'GET' and use_recaptcha:
        session['form_loaded_at'] = datetime.utcnow().isoformat()
    
    return render_template('main/contact.html', form=form)

@bp.route('/terminal')
@bp.route('/terminal/')
def terminal():
    """Interactive terminal interface."""
    return render_template('main/terminal.html')

# API endpoints for terminal commands
@bp.route('/api/terminal/help')
def terminal_help():
    """API endpoint that returns a dictionary of available terminal commands and their descriptions.
    
    Returns:
        dict: Dictionary with 'commands' key containing command descriptions
    """
    commands = {
        'help': 'Show this help message',
        'about': 'Display information about David',
        'portfolio': 'List my projects',
        'blog': 'Show recent blog posts',
        'contact': 'Display contact information',
        'social': 'Show social media links',
        'skills': 'List my technical skills',
        'clear': 'Clear the terminal',
        'whoami': 'Display current user info',
        'ls': 'List available sections',
        'cat <section>': 'Display content of a section'
    }
    return {'commands': commands}

# API endpoints for GitHub stats
@bp.route('/api/github/stats')
def github_stats_api():
    """API endpoint that fetches GitHub statistics including commit count and profile data.
    
    Returns:
        dict: JSON response containing commits, profile stats, and username
    """
    commits = github_stats.get_commits_this_month()
    profile = github_stats.get_profile_stats()
    repos = github_stats.get_user_repos()
    
    # Add actual total repo count (includes private if authenticated)
    profile['total_repos'] = len(repos) if repos else profile.get('public_repos', 0)
    
    return {
        'commits': commits,
        'profile': profile,
        'username': github_stats.username
    }

@bp.route('/api/github/activity')
def github_activity_api():
    """API endpoint that fetches recent GitHub activity for the past 30 days.
    
    Returns:
        dict: JSON response containing recent commit activity data
    """
    activity = github_stats.get_recent_activity(days=30)
    return {'activity': activity}

@bp.route('/api/terminal/command/<command>')
def terminal_command(command):
    """API endpoint that processes terminal commands and returns appropriate responses.
    
    Args:
        command (str): The terminal command to process
        
    Returns:
        dict: JSON response with command output
    """
    
    responses = {
        'about': {
            'output': [
                'Full-Stack Founder and Digital Nomad',
                '',
                'Building innovative web applications and digital experiences.',
                'Passionate about clean code, user experience, and emerging technologies.',
                '',
                'Currently working on:',
                '• CRM Baby - Next-gen customer relationship management',
                '• App Launcher - Streamlined application deployment',
                '• Mix Convert Keyword - AI-powered keyword optimization',
                '',
                'Type "portfolio" to see my projects or "contact" for my details.'
            ]
        },
        'portfolio': {
            'output': [
                'Active Projects:',
                '',
                '1. CRM Baby (https://www.crmbaby.com)',
                '   Advanced CRM with AI-powered insights',
                '   Tech: Python, Flask, AI/ML, PostgreSQL',
                '',
                '2. App Launcher (https://www.applauncher.io)',
                '   Application deployment platform',
                '   Tech: Docker, Kubernetes, React, Node.js',
                '',
                '3. Mix Convert Keyword (https://www.mix-convert-keyword.com)',
                '   Keyword research and optimization tool',
                '   Tech: Python, NLP, Vue.js, Redis',
                '',
                'Type "cat portfolio" for detailed project information.'
            ]
        },
        'contact': {
            'output': [
                'Contact Information:',
                '',
                '📧 Email: Available on request',
                '🐙 GitHub: ' + current_app.config.get('GITHUB_URL', '#'),
                '🐦 Twitter: ' + current_app.config.get('TWITTER_URL', '#'),
                '💼 LinkedIn: ' + current_app.config.get('LINKEDIN_URL', '#'),
                '',
                'Or use the contact form at /contact'
            ]
        },
        'social': {
            'output': [
                'Social Media & Links:',
                '',
                '🐙 GitHub: ' + current_app.config.get('GITHUB_URL', '#'),
                '🐦 Twitter: ' + current_app.config.get('TWITTER_URL', '#'),
                '💼 LinkedIn: ' + current_app.config.get('LINKEDIN_URL', '#'),
                '',
                'Follow me for updates on my latest projects!'
            ]
        },
        'skills': {
            'output': [
                'Technical Skills:',
                '',
                '🐍 Backend: Python, Flask, Django, FastAPI',
                '⚛️  Frontend: React, Vue.js, JavaScript, TypeScript',
                '🗄️  Databases: PostgreSQL, MongoDB, Redis',
                '☁️  Cloud: AWS, Docker, Kubernetes',
                '🤖 AI/ML: Machine Learning, NLP, Data Analysis',
                '🛠️  Tools: Git, Linux, Docker, CI/CD',
                '',
                'Always learning and exploring new technologies!'
            ]
        },
        'whoami': {
            'output': [
                'guest@dcblack.co.uk',
                '',
                'You are browsing the personal terminal of a',
                'Full-Stack Founder and Digital Nomad.',
                '',
                'Current location: The Internet',
                'Status: Making apps for fun and profit'
            ]
        },
        'ls': {
            'output': [
                'Available sections:',
                '',
                'drwxr-xr-x  about/',
                'drwxr-xr-x  portfolio/',
                'drwxr-xr-x  blog/',
                'drwxr-xr-x  contact/',
                'drwxr-xr-x  social/',
                'drwxr-xr-x  skills/',
                '',
                'Use "cat <section>" to view contents'
            ]
        }
    }
    
    if command in responses:
        return responses[command]
    else:
        return {
            'output': [
                f'Command not found: {command}',
                '',
                'Type "help" for available commands.'
            ]
        }