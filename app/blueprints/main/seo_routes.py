"""
SEO-related routes for robots.txt, sitemap.xml, and other SEO utilities.
"""

from flask import current_app, render_template_string, url_for
from app.blueprints.main import bp
from app.models import BlogPost, PortfolioItem
from datetime import datetime


@bp.route('/robots.txt')
def robots_txt():
    """Generate robots.txt file for search engine crawlers."""
    robots_content = f"""User-agent: *
Allow: /

# Sitemaps
Sitemap: {url_for('main.sitemap_xml', _external=True)}

# Crawl-delay
Crawl-delay: 1

# Disallow admin areas
Disallow: /admin/
Disallow: /auth/
Disallow: /api/

# Allow specific areas
Allow: /blog/
Allow: /portfolio/
Allow: /contact/
Allow: /terminal/
"""
    
    return robots_content, 200, {'Content-Type': 'text/plain'}


@bp.route('/sitemap.xml')
def sitemap_xml():
    """Generate XML sitemap for search engines."""
    
    # Get all published blog posts
    blog_posts = BlogPost.query.filter_by(is_published=True).all()
    
    # Get all portfolio items
    portfolio_items = PortfolioItem.query.all()
    
    # Static pages
    static_pages = [
        {
            'url': url_for('main.index', _external=True),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '1.0'
        },
        {
            'url': url_for('main.about', _external=True),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.8'
        },
        {
            'url': url_for('main.portfolio', _external=True),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.9'
        },
        {
            'url': url_for('main.contact', _external=True),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        },
        {
            'url': url_for('main.terminal', _external=True),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.6'
        },
        {
            'url': url_for('blog.index', _external=True),
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '0.9'
        }
    ]
    
    # Add blog posts
    blog_urls = []
    for post in blog_posts:
        blog_urls.append({
            'url': url_for('blog.post', slug=post.slug, _external=True),
            'lastmod': post.updated_at.strftime('%Y-%m-%d') if post.updated_at else post.created_at.strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.8'
        })
    
    sitemap_template = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {% for page in static_pages %}
    <url>
        <loc>{{ page.url }}</loc>
        <lastmod>{{ page.lastmod }}</lastmod>
        <changefreq>{{ page.changefreq }}</changefreq>
        <priority>{{ page.priority }}</priority>
    </url>
    {% endfor %}
    {% for post in blog_urls %}
    <url>
        <loc>{{ post.url }}</loc>
        <lastmod>{{ post.lastmod }}</lastmod>
        <changefreq>{{ post.changefreq }}</changefreq>
        <priority>{{ post.priority }}</priority>
    </url>
    {% endfor %}
</urlset>"""
    
    xml_content = render_template_string(
        sitemap_template,
        static_pages=static_pages,
        blog_urls=blog_urls
    )
    
    return xml_content, 200, {'Content-Type': 'application/xml'}


@bp.route('/manifest.json')
def manifest_json():
    """Generate web app manifest for PWA capabilities."""
    manifest = {
        "name": f"{current_app.config['SITE_NAME']} - Terminal Interface",
        "short_name": current_app.config['SITE_NAME'],
        "description": current_app.config['SITE_TAGLINE'],
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000012",
        "theme_color": "#00ff00",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": url_for('static', filename='images/icon-192.png'),
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": url_for('static', filename='images/icon-512.png'),
                "sizes": "512x512",
                "type": "image/png"
            }
        ],
        "categories": ["developer", "portfolio", "blog"],
        "lang": "en"
    }
    
    return manifest, 200, {'Content-Type': 'application/json'}