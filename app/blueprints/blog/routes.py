"""
Blog blueprint routes for the terminal blog system.
"""

from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from app.blueprints.blog import bp
from app.models import BlogPost, Tag
from app.forms import SearchForm
from app import db
from sqlalchemy import or_

@bp.route('/')
def index():
    """Blog index page displaying paginated list of published posts with optional filtering.
    
    Supports query parameters:
    - page: Page number for pagination
    - tag: Filter posts by tag slug
    - q: Search query to filter posts by title/content
    
    Returns:
        Rendered blog index template with posts, tags, and search form
    """
    page = request.args.get('page', 1, type=int)
    tag_slug = request.args.get('tag')
    search_query = request.args.get('q')
    
    # Base query for published posts
    query = BlogPost.query.filter_by(is_published=True)
    
    # Filter by tag if provided
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
        query = query.filter(BlogPost.tags.contains(tag))
    
    # Filter by search query if provided
    if search_query:
        query = query.filter(
            or_(
                BlogPost.title.contains(search_query),
                BlogPost.content.contains(search_query),
                BlogPost.excerpt.contains(search_query)
            )
        )
    
    # Order by publication date and paginate
    posts = query.order_by(BlogPost.published_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    
    # Get all tags for sidebar
    tags = Tag.query.all()
    
    # Search form
    search_form = SearchForm()
    if search_query:
        search_form.query.data = search_query
    
    return render_template('blog/index.html', 
                         posts=posts, 
                         tags=tags, 
                         search_form=search_form,
                         current_tag=tag_slug,
                         search_query=search_query)

@bp.route('/post/<slug>')
def post(slug):
    """Display individual blog post by slug and increment view count.
    
    Args:
        slug (str): Unique slug identifier for the blog post
        
    Returns:
        Rendered blog post template with post data and related posts
    """
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Increment view count
    post.increment_views()
    
    # Get related posts (same tags, excluding current post)
    related_posts = []
    if post.tags:
        related_posts = BlogPost.query.filter(
            BlogPost.tags.any(Tag.id.in_([tag.id for tag in post.tags])),
            BlogPost.id != post.id,
            BlogPost.is_published == True
        ).limit(3).all()
    
    return render_template('blog/post.html', 
                         post=post, 
                         related_posts=related_posts)

@bp.route('/tag/<slug>')
def tag(slug):
    """Posts filtered by tag."""
    return redirect(url_for('blog.index', tag=slug))

@bp.route('/search')
def search():
    """Search posts."""
    query = request.args.get('q', '')
    if query:
        return redirect(url_for('blog.index', q=query))
    return redirect(url_for('blog.index'))

@bp.route('/api/posts')
def api_posts():
    """API endpoint that returns recent published blog posts in JSON format.
    
    Used for terminal integration to display blog posts in the command interface.
    
    Returns:
        JSON response with list of 5 most recent published posts
    """
    posts = BlogPost.query.filter_by(is_published=True)\
                          .order_by(BlogPost.published_at.desc())\
                          .limit(5).all()
    
    return jsonify({
        'posts': [{
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'published_at': post.published_at.strftime('%Y-%m-%d') if post.published_at else None,
            'reading_time': post.reading_time,
            'view_count': post.view_count
        } for post in posts]
    })

@bp.route('/feed')
def feed():
    """RSS feed for blog posts."""
    posts = BlogPost.query.filter_by(is_published=True)\
                          .order_by(BlogPost.published_at.desc())\
                          .limit(20).all()
    
    return render_template('blog/feed.xml', posts=posts), 200, {
        'Content-Type': 'application/rss+xml; charset=utf-8'
    }