#!/usr/bin/env python3
"""
Main application entry point for the hacker terminal personal brand page.
Run with: python run.py
"""

import os
from app import create_app, db
from app.models import User, BlogPost, PortfolioItem

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell."""
    return {
        'db': db,
        'User': User,
        'BlogPost': BlogPost,
        'PortfolioItem': PortfolioItem
    }

@app.cli.command()
def init_db():
    """Initialize the database with sample data."""
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')  # Change this in production!
        db.session.add(admin)
    
    # Add portfolio items
    portfolio_items = [
        {
            'title': 'CRM Baby',
            'description': 'Advanced Customer Relationship Management system with AI-powered insights',
            'url': 'https://www.crmbaby.com',
            'technologies': 'Python, Flask, AI/ML, PostgreSQL',
            'status': 'live'
        },
        {
            'title': 'App Launcher',
            'description': 'Streamlined application deployment and management platform',
            'url': 'https://www.applauncher.io',
            'technologies': 'Docker, Kubernetes, React, Node.js',
            'status': 'live'
        },
        {
            'title': 'Mix Convert Keyword',
            'description': 'Intelligent keyword research and conversion optimization tool',
            'url': 'https://www.mix-convert-keyword.com',
            'technologies': 'Python, NLP, Vue.js, Redis',
            'status': 'live'
        }
    ]
    
    for item_data in portfolio_items:
        existing = PortfolioItem.query.filter_by(title=item_data['title']).first()
        if not existing:
            item = PortfolioItem(**item_data)
            db.session.add(item)
    
    # Add a sample blog post
    sample_post = BlogPost.query.filter_by(title='Welcome to the Terminal').first()
    if not sample_post:
        post = BlogPost(
            title='Welcome to the Terminal',
            content='''# Welcome to My Digital Terminal

This is where I share my thoughts on technology, development, and the art of building digital experiences.

## Currently Working On

- Building next-generation CRM solutions
- Exploring AI/ML applications in business automation
- Contributing to open-source projects

## Philosophy

> "Code is poetry written in logic"

I believe in creating software that not only works but inspires. Every line of code is an opportunity to solve problems and make the digital world a little bit better.

Stay tuned for more insights from the terminal...

---

*System initialized. Ready for input.*
            ''',
            author_id=1,
            is_published=True
        )
        db.session.add(post)
    
    db.session.commit()
    print("Database initialized successfully!")

if __name__ == '__main__':
    # Enable debug mode for development - disable in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'on']
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)