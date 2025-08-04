"""
Authentication blueprint routes.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.blueprints.auth import bp
from app.models import User
from app.forms import LoginForm
from app import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user authentication with terminal-style login interface.
    
    GET: Display login form
    POST: Process login credentials and authenticate user
    
    Returns:
        On GET: Rendered login template
        On successful POST: Redirect to admin dashboard or intended page
        On failed POST: Re-render login form with error message
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            flash('Access granted. Welcome to the system.', 'success')
            
            # Redirect to intended page or admin dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin.dashboard')
            
            return redirect(next_page)
        else:
            flash('Authentication failed. Access denied.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to homepage.
    
    Requires user to be logged in.
    
    Returns:
        Redirect to main index page with logout confirmation message
    """
    logout_user()
    flash('Session terminated. Goodbye.', 'info')
    return redirect(url_for('main.index'))