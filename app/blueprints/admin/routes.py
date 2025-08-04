"""
Admin blueprint routes for blog and portfolio management.
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.admin import bp
from app.models import BlogPost, PortfolioItem, Tag, ContactMessage
from app.forms import BlogPostForm, PortfolioItemForm, TagForm
from app import db
from datetime import datetime

def admin_required(f):
    """Decorator function that ensures only admin users can access protected routes.
    
    Checks that the current user is both authenticated and has admin privileges.
    Raises 403 Forbidden error if access is denied.
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function with admin access control
    """
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard displaying site statistics and recent activity.
    
    Shows:
    - Total, published, and draft post counts
    - Portfolio item count
    - Unread contact messages count
    - Recent posts and messages
    
    Returns:
        Rendered admin dashboard template with statistics and activity data
    """
    # Get statistics
    total_posts = BlogPost.query.count()
    published_posts = BlogPost.query.filter_by(is_published=True).count()
    draft_posts = total_posts - published_posts
    total_portfolio = PortfolioItem.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    
    # Recent activity
    recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         stats={
                             'total_posts': total_posts,
                             'published_posts': published_posts,
                             'draft_posts': draft_posts,
                             'total_portfolio': total_portfolio,
                             'unread_messages': unread_messages
                         },
                         recent_posts=recent_posts,
                         recent_messages=recent_messages)

# Blog Post Management
@bp.route('/posts')
@login_required
@admin_required
def posts():
    """List all blog posts."""
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/posts.html', posts=posts)

@bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_post():
    """Create a new blog post."""
    form = BlogPostForm()
    
    if form.validate_on_submit():
        post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            author_id=current_user.id,
            is_published=form.is_published.data
        )
        
        if form.is_published.data:
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.flush()  # Get the post ID
        
        # Handle tags
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',')]
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
        
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/edit_post.html', form=form, post=None)

@bp.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    """Edit an existing blog post."""
    post = BlogPost.query.get_or_404(id)
    form = BlogPostForm(obj=post)
    
    # Pre-populate tags
    if post.tags:
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.meta_description = form.meta_description.data
        post.meta_keywords = form.meta_keywords.data
        post.updated_at = datetime.utcnow()
        
        # Handle publication status
        if form.is_published.data and not post.is_published:
            post.publish()
        elif not form.is_published.data and post.is_published:
            post.unpublish()
        
        # Clear existing tags and add new ones
        post.tags.clear()
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',')]
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/edit_post.html', form=form, post=post)

@bp.route('/posts/delete/<int:id>')
@login_required
@admin_required
def delete_post(id):
    """Delete a blog post."""
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin.posts'))

@bp.route('/posts/toggle-publish/<int:id>')
@login_required
@admin_required
def toggle_publish(id):
    """Toggle the publication status of a blog post between published and draft.
    
    Args:
        id (int): Blog post ID to toggle
        
    Returns:
        Redirect to admin posts list with status update message
    """
    post = BlogPost.query.get_or_404(id)
    
    if post.is_published:
        post.unpublish()
        flash('Post unpublished.', 'info')
    else:
        post.publish()
        flash('Post published.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.posts'))

# Portfolio Management
@bp.route('/portfolio')
@login_required
@admin_required
def portfolio():
    """Manage portfolio items."""
    items = PortfolioItem.query.order_by(PortfolioItem.sort_order).all()
    return render_template('admin/portfolio.html', items=items)

@bp.route('/portfolio/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_portfolio_item():
    """Create a new portfolio item."""
    form = PortfolioItemForm()
    
    if form.validate_on_submit():
        item = PortfolioItem(
            title=form.title.data,
            description=form.description.data,
            url=form.url.data,
            github_url=form.github_url.data,
            image_url=form.image_url.data,
            technologies=form.technologies.data,
            status=form.status.data,
            is_featured=form.is_featured.data,
            sort_order=int(form.sort_order.data) if form.sort_order.data else 0
        )
        
        db.session.add(item)
        db.session.commit()
        flash('Portfolio item created successfully!', 'success')
        return redirect(url_for('admin.portfolio'))
    
    return render_template('admin/edit_portfolio.html', form=form, item=None)

@bp.route('/portfolio/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_portfolio_item(id):
    """Edit a portfolio item."""
    item = PortfolioItem.query.get_or_404(id)
    form = PortfolioItemForm(obj=item)
    
    if form.validate_on_submit():
        item.title = form.title.data
        item.description = form.description.data
        item.url = form.url.data
        item.github_url = form.github_url.data
        item.image_url = form.image_url.data
        item.technologies = form.technologies.data
        item.status = form.status.data
        item.is_featured = form.is_featured.data
        item.sort_order = int(form.sort_order.data) if form.sort_order.data else 0
        item.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Portfolio item updated successfully!', 'success')
        return redirect(url_for('admin.portfolio'))
    
    return render_template('admin/edit_portfolio.html', form=form, item=item)

@bp.route('/portfolio/delete/<int:id>')
@login_required
@admin_required
def delete_portfolio_item(id):
    """Delete a portfolio item."""
    item = PortfolioItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Portfolio item deleted successfully!', 'success')
    return redirect(url_for('admin.portfolio'))

# Tags Management
@bp.route('/tags')
@login_required
@admin_required
def tags():
    """Manage blog tags."""
    tags = Tag.query.all()
    return render_template('admin/tags.html', tags=tags)

@bp.route('/tags/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_tag():
    """Create a new tag."""
    form = TagForm()
    
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data,
            description=form.description.data,
            color=form.color.data or '#00ff00'
        )
        
        db.session.add(tag)
        db.session.commit()
        flash('Tag created successfully!', 'success')
        return redirect(url_for('admin.tags'))
    
    return render_template('admin/edit_tag.html', form=form, tag=None)

@bp.route('/tags/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tag(id):
    """Edit a tag."""
    tag = Tag.query.get_or_404(id)
    form = TagForm(obj=tag)
    
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.description = form.description.data
        tag.color = form.color.data or '#00ff00'
        
        db.session.commit()
        flash('Tag updated successfully!', 'success')
        return redirect(url_for('admin.tags'))
    
    return render_template('admin/edit_tag.html', form=form, tag=tag)

@bp.route('/tags/delete/<int:id>')
@login_required
@admin_required
def delete_tag(id):
    """Delete a tag."""
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted successfully!', 'success')
    return redirect(url_for('admin.tags'))

# Messages Management
@bp.route('/messages')
@login_required
@admin_required
def messages():
    """View contact messages."""
    page = request.args.get('page', 1, type=int)
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/messages.html', messages=messages)

@bp.route('/messages/read/<int:id>')
@login_required
@admin_required
def mark_message_read(id):
    """Mark a message as read."""
    message = ContactMessage.query.get_or_404(id)
    message.mark_as_read()
    return redirect(url_for('admin.messages'))

@bp.route('/messages/delete/<int:id>')
@login_required
@admin_required
def delete_message(id):
    """Delete a contact message."""
    message = ContactMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin.messages'))