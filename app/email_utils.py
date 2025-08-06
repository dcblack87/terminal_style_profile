"""
Email utilities for sending contact form messages and other notifications.
"""

from flask import current_app, render_template_string
from flask_mail import Message
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_contact_form_email(name, email, subject, message):
    """
    Send contact form submission to the configured contact email.
    
    Args:
        name (str): Sender's name
        email (str): Sender's email
        subject (str): Message subject
        message (str): Message content
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email template for contact form
        email_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>New Contact Form Submission</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8f9fa; 
            color: #333333; 
            margin: 0; 
            padding: 20px; 
            line-height: 1.6;
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background-color: #ffffff; 
            border: 2px solid #28a745; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white; 
            padding: 25px 30px;
            text-align: center;
        }
        .header h2 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .content {
            padding: 30px;
        }
        .field { 
            margin-bottom: 20px; 
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 15px;
        }
        .field:last-of-type {
            border-bottom: none;
        }
        .field-label { 
            color: #28a745; 
            font-weight: 600; 
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px; 
            display: flex;
            align-items: center;
        }
        .field-label span {
            margin-left: 8px;
        }
        .field-value { 
            background-color: #f8f9fa; 
            padding: 15px; 
            border: 1px solid #dee2e6; 
            border-radius: 6px; 
            white-space: pre-wrap; 
            font-size: 15px;
            color: #495057;
        }
        .field-value.email {
            color: #28a745;
            font-weight: 500;
        }
        .footer { 
            background-color: #f8f9fa;
            padding: 20px 30px; 
            border-top: 1px solid #dee2e6;
            font-size: 13px; 
            color: #6c757d; 
            text-align: center;
        }
        .footer p {
            margin: 5px 0;
        }
        .reply-info {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 12px;
            border-radius: 6px;
            margin-top: 10px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📧 New Contact Form Submission</h2>
        </div>
        
        <div class="content">
            <div class="field">
                <div class="field-label">
                    👤 <span>From</span>
                </div>
                <div class="field-value">{{ name }}</div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    📧 <span>Email</span>
                </div>
                <div class="field-value email">{{ email }}</div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    📝 <span>Subject</span>
                </div>
                <div class="field-value">{{ subject or 'No subject provided' }}</div>
            </div>
            
            <div class="field">
                <div class="field-label">
                    💬 <span>Message</span>
                </div>
                <div class="field-value">{{ message }}</div>
            </div>
            
            <div class="reply-info">
                💡 Reply directly to this email to respond to {{ name }}
            </div>
        </div>
        
        <div class="footer">
            <p>This message was sent via the contact form on <strong>dcblack.co.uk</strong></p>
            <p>Received on {{ now.strftime('%B %d, %Y at %I:%M %p UTC') if now else 'just now' }}</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Plain text version
        text_template = """
New Contact Form Submission
==========================

From: {{ name }}
Email: {{ email }}
Subject: {{ subject or 'No subject provided' }}

Message:
{{ message }}

---
This message was sent via the contact form on dcblack.co.uk
Reply directly to this email to respond to {{ name }}.
        """
        
        # Render templates
        from datetime import datetime
        html_body = render_template_string(email_template, 
                                         name=name, 
                                         email=email, 
                                         subject=subject, 
                                         message=message,
                                         now=datetime.utcnow())
        
        text_body = render_template_string(text_template, 
                                         name=name, 
                                         email=email, 
                                         subject=subject, 
                                         message=message)
        
        # Create email message
        msg = Message(
            subject=f"Contact Form: {subject}" if subject else f"Contact Form Message from {name}",
            recipients=[current_app.config['CONTACT_EMAIL']],
            html=html_body,
            body=text_body,
            reply_to=email
        )
        
        # Send email
        from app import mail
        mail.send(msg)
        
        logger.info(f"Contact form email sent successfully from {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send contact form email: {str(e)}")
        return False

def send_contact_confirmation_email(name, email):
    """
    Send a confirmation email to the person who submitted the contact form.
    
    Args:
        name (str): Sender's name
        email (str): Sender's email
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Confirmation email template
        confirmation_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Message Received - David Black</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8f9fa; 
            color: #333333; 
            margin: 0; 
            padding: 20px; 
            line-height: 1.6;
        }
        .container { 
            max-width: 600px; 
            margin: 0 auto; 
            background-color: #ffffff; 
            border: 2px solid #28a745; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white; 
            padding: 25px 30px;
            text-align: center;
        }
        .header h2 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .content { 
            padding: 30px;
            font-size: 16px;
        }
        .content p {
            margin-bottom: 16px;
        }
        .content ul {
            margin: 20px 0;
            padding-left: 0;
            list-style: none;
        }
        .content li {
            margin-bottom: 10px;
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #28a745;
        }
        .content a {
            color: #28a745;
            text-decoration: none;
            font-weight: 500;
        }
        .content a:hover {
            text-decoration: underline;
        }
        .signature {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 25px;
            border-left: 4px solid #28a745;
        }
        .signature p {
            margin: 0;
            color: #495057;
        }
        .signature .name {
            font-weight: 600;
            color: #28a745;
            font-size: 18px;
        }
        .signature .title {
            color: #6c757d;
            font-style: italic;
        }
        .footer { 
            background-color: #f8f9fa;
            padding: 20px 30px; 
            border-top: 1px solid #dee2e6;
            font-size: 13px; 
            color: #6c757d; 
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✅ Message Received</h2>
        </div>
        
        <div class="content">
            <p>Hi <strong>{{ name }}</strong>,</p>
            
            <p>Thanks for reaching out! I've received your message and will get back to you within <strong>24-48 hours</strong>.</p>
            
            <p>In the meantime, feel free to check out my projects and latest updates:</p>
            <ul>
                <li>🐙 <a href="https://github.com/dcblack87">GitHub</a> - My latest code and open source projects</li>
                <li>🐦 <a href="https://twitter.com/davidwentnomad">Twitter</a> - Tech insights and updates</li>
                <li>💼 <a href="https://linkedin.com/in/dcblack">LinkedIn</a> - Professional network and career updates</li>
            </ul>
            
            <div class="signature">
                <p class="name">David Black</p>
                <p class="title">Full-Stack Founder and Digital Nomad</p>
                <p style="margin-top: 10px; font-size: 14px;">Making apps for fun and profit from Thailand 🇹🇭</p>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated confirmation. Please don't reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Plain text version
        text_confirmation = """
Message Received
================

Hi {{ name }},

Thanks for reaching out! I've received your message and will get back to you within 24-48 hours.

In the meantime, feel free to check out my projects and latest updates on:
• GitHub: https://github.com/dcblack
• LinkedIn: https://linkedin.com/in/dcblack

Best regards,
David Black
Full-Stack Founder and Digital Nomad

---
This is an automated confirmation. Please don't reply to this email.
        """
        
        # Render templates
        html_body = render_template_string(confirmation_template, name=name)
        text_body = render_template_string(text_confirmation, name=name)
        
        # Create confirmation email
        msg = Message(
            subject="Thanks for your message!",
            recipients=[email],
            html=html_body,
            body=text_body
        )
        
        # Send email
        from app import mail
        mail.send(msg)
        
        logger.info(f"Confirmation email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        return False