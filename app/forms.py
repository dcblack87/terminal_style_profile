"""
WTForms for the hacker terminal personal brand page.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL
from wtforms.widgets import TextArea
from app.models import User, Tag

class LoginForm(FlaskForm):
    """Login form for user authentication."""
    username = StringField('Username', validators=[DataRequired()], 
                          render_kw={'placeholder': 'Enter username', 'class': 'terminal-input'})
    password = PasswordField('Password', validators=[DataRequired()], 
                           render_kw={'placeholder': 'Enter password', 'class': 'terminal-input'})
    remember_me = BooleanField('Remember Me')
    submit = StringField('Login', render_kw={'class': 'terminal-button', 'value': 'access granted'})

class ContactForm(FlaskForm):
    """Contact form for visitor inquiries."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)],
                      render_kw={'placeholder': 'Your name', 'class': 'terminal-input'})
    email = StringField('Email', validators=[DataRequired(), Email()],
                       render_kw={'placeholder': 'your.email@domain.com', 'class': 'terminal-input'})
    subject = StringField('Subject', validators=[Optional(), Length(max=200)],
                         render_kw={'placeholder': 'Message subject', 'class': 'terminal-input'})
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)],
                           render_kw={'placeholder': 'Your message...', 'class': 'terminal-textarea', 'rows': 8})
    submit = StringField('Send Message', render_kw={'class': 'terminal-button', 'value': 'transmit'})

class BlogPostForm(FlaskForm):
    """Form for creating and editing blog posts."""
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)],
                       render_kw={'placeholder': 'Enter post title', 'class': 'terminal-input'})
    content = TextAreaField('Content', validators=[DataRequired()],
                           render_kw={'placeholder': 'Write your post content...', 'class': 'terminal-textarea', 'rows': 20})
    excerpt = TextAreaField('Excerpt', validators=[Optional()],
                           render_kw={'placeholder': 'Brief description (optional)', 'class': 'terminal-textarea', 'rows': 3})
    meta_description = StringField('Meta Description', validators=[Optional(), Length(max=160)],
                                  render_kw={'placeholder': 'SEO meta description', 'class': 'terminal-input'})
    meta_keywords = StringField('Meta Keywords', validators=[Optional()],
                               render_kw={'placeholder': 'keyword1, keyword2, keyword3', 'class': 'terminal-input'})
    is_published = BooleanField('Publish immediately')
    tags = StringField('Tags', validators=[Optional()],
                      render_kw={'placeholder': 'tag1, tag2, tag3', 'class': 'terminal-input'})
    submit = StringField('Save Post', render_kw={'class': 'terminal-button', 'value': 'save'})

class PortfolioItemForm(FlaskForm):
    """Form for managing portfolio items."""
    title = StringField('Project Title', validators=[DataRequired(), Length(min=2, max=100)],
                       render_kw={'placeholder': 'Project name', 'class': 'terminal-input'})
    description = TextAreaField('Description', validators=[DataRequired()],
                               render_kw={'placeholder': 'Project description...', 'class': 'terminal-textarea', 'rows': 5})
    url = StringField('Live URL', validators=[Optional(), URL()],
                     render_kw={'placeholder': 'https://example.com', 'class': 'terminal-input'})
    github_url = StringField('GitHub URL', validators=[Optional(), URL()],
                            render_kw={'placeholder': 'https://github.com/user/repo', 'class': 'terminal-input'})
    image_url = StringField('Image URL', validators=[Optional(), URL()],
                           render_kw={'placeholder': 'https://example.com/image.jpg', 'class': 'terminal-input'})
    technologies = StringField('Technologies', validators=[Optional()],
                              render_kw={'placeholder': 'Python, Flask, React, etc.', 'class': 'terminal-input'})
    status = SelectField('Status', choices=[
        ('live', 'Live'),
        ('development', 'In Development'),
        ('archived', 'Archived')
    ], default='live')
    is_featured = BooleanField('Featured Project')
    sort_order = StringField('Sort Order', validators=[Optional()],
                            render_kw={'placeholder': '0', 'class': 'terminal-input'})
    submit = StringField('Save Project', render_kw={'class': 'terminal-button', 'value': 'save'})

class TagForm(FlaskForm):
    """Form for managing blog tags."""
    name = StringField('Tag Name', validators=[DataRequired(), Length(min=2, max=50)],
                      render_kw={'placeholder': 'Tag name', 'class': 'terminal-input'})
    description = TextAreaField('Description', validators=[Optional()],
                               render_kw={'placeholder': 'Tag description...', 'class': 'terminal-textarea', 'rows': 3})
    color = StringField('Color', validators=[Optional()],
                       render_kw={'placeholder': '#00ff00', 'class': 'terminal-input'})
    submit = StringField('Save Tag', render_kw={'class': 'terminal-button', 'value': 'save'})

class SearchForm(FlaskForm):
    """Search form for blog posts."""
    query = StringField('Search', validators=[DataRequired()],
                       render_kw={'placeholder': 'Search posts...', 'class': 'terminal-input'})
    submit = StringField('Search', render_kw={'class': 'terminal-button', 'value': 'search'})

class TerminalCommandForm(FlaskForm):
    """Form for terminal command input."""
    command = StringField('Command', validators=[DataRequired()],
                         render_kw={'placeholder': 'Type a command...', 'class': 'terminal-command-input', 'autocomplete': 'off'})
    submit = HiddenField()