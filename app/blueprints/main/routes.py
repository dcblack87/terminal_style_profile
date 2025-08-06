"""
Main blueprint routes for the hacker terminal personal brand page.
"""

from flask import render_template, request, flash, redirect, url_for, current_app
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
    """Contact form page."""
    # Use reCAPTCHA form if available and configured
    use_recaptcha = (RECAPTCHA_FORM_AVAILABLE and 
                    current_app.config.get('RECAPTCHA_PUBLIC_KEY') and 
                    current_app.config.get('RECAPTCHA_PRIVATE_KEY'))
    
    if use_recaptcha:
        form = ContactFormWithRecaptcha()
    else:
        form = ContactForm()
    
    if form.validate_on_submit():
        # Create new contact message
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        
        db.session.add(message)
        
        try:
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
            
            db.session.commit()
            
            if email_sent:
                flash('Message sent successfully! I\'ll get back to you soon.', 'success')
            else:
                flash('Message saved but email notification failed. I\'ll still see your message and respond soon.', 'warning')
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Contact form error: {str(e)}")
            flash('There was an error sending your message. Please try again or contact me directly.', 'error')
            
        return redirect(url_for('main.contact'))
    
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