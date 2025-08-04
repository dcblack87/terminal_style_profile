"""
Database models for the hacker terminal personal brand page.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from app import db

class User(UserMixin, db.Model):
    """User model for authentication and blog management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    blog_posts = db.relationship('BlogPost', backref='author', lazy='dynamic', 
                                cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

class BlogPost(db.Model):
    """Blog post model for the terminal blog system."""
    
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, index=True)
    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # SEO fields
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    # Analytics
    view_count = db.Column(db.Integer, default=0)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    tags = db.relationship('Tag', secondary='post_tags', backref='posts', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(BlogPost, self).__init__(**kwargs)
        if not self.slug and self.title:
            self.generate_slug()
        if not self.excerpt and self.content:
            self.generate_excerpt()
    
    def generate_slug(self):
        """Generate a unique URL-friendly slug from the blog post title.
        
        Creates a slugified version of the title and ensures uniqueness by
        appending a counter if a post with the same slug already exists.
        """
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        self.slug = slug
    
    def generate_excerpt(self, length=200):
        """Generate a short excerpt from the blog post content for previews.
        
        Args:
            length (int): Maximum length of the excerpt in characters (default: 200)
            
        Sets the excerpt property to a truncated version of the content.
        """
        if len(self.content) <= length:
            self.excerpt = self.content
        else:
            self.excerpt = self.content[:length].rsplit(' ', 1)[0] + '...'
    
    def publish(self):
        """Publish the blog post."""
        self.is_published = True
        self.published_at = datetime.utcnow()
    
    def unpublish(self):
        """Unpublish the blog post."""
        self.is_published = False
        self.published_at = None
    
    def increment_views(self):
        """Increment the view count."""
        self.view_count += 1
        db.session.commit()
    
    @property
    def reading_time(self):
        """Calculate estimated reading time based on average reading speed.
        
        Uses the standard assumption of 200 words per minute reading speed.
        
        Returns:
            int: Estimated reading time in minutes (minimum 1 minute)
        """
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'

class Tag(db.Model):
    """Tag model for categorizing blog posts."""
    
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#00ff00')  # Terminal green default
    
    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = slugify(self.name)
    
    def __repr__(self):
        return f'<Tag {self.name}>'

# Association table for many-to-many relationship between posts and tags
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class PortfolioItem(db.Model):
    """Portfolio item model for showcasing projects."""
    
    __tablename__ = 'portfolio_items'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    technologies = db.Column(db.String(255))  # Comma-separated list
    status = db.Column(db.String(20), default='live')  # live, development, archived
    sort_order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def tech_list(self):
        """Parse the comma-separated technologies string into a list.
        
        Returns:
            list: List of technology strings, empty list if no technologies set
        """
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',')]
        return []
    
    @property
    def status_color(self):
        """Get the terminal-theme color code for the project status.
        
        Returns different colors for different project statuses:
        - live: Green (#00ff00)
        - development: Yellow (#ffff00) 
        - archived: Gray (#888888)
        
        Returns:
            str: Hex color code for the status
        """
        colors = {
            'live': '#00ff00',      # Green
            'development': '#ffff00',  # Yellow
            'archived': '#888888'    # Gray
        }
        return colors.get(self.status, '#00ff00')
    
    def __repr__(self):
        return f'<PortfolioItem {self.title}>'

class ContactMessage(db.Model):
    """Contact message model for storing inquiries."""
    
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def mark_as_read(self):
        """Mark the message as read."""
        self.is_read = True
        db.session.commit()
    
    def __repr__(self):
        return f'<ContactMessage from {self.name}>'