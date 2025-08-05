# Terminal Portfolio & Blog Platform

A sleek, terminal-themed personal portfolio and blog platform built with Flask. Perfect for developers, engineers, and tech professionals who want to showcase their work with a distinctive hacker aesthetic.

![Terminal Theme](https://img.shields.io/badge/Theme-Terminal-00ff00?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.7+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3+-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## 📚 Table of Contents
- [Live Demo](#-live-demo)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Customization](#-customization)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Development](#-development)
- [Support](#-support)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)


## 🌐 Live Demo

**See it in action:** [https://www.dcblack.co.uk](https://www.dcblack.co.uk)

Experience the full terminal-themed interface, interactive commands, portfolio showcase, and blog system as used by the template's creator. This live site demonstrates all features including the admin panel workflow, GitHub integration, and responsive design.

## ✨ Features

### 🖥️ **Terminal-Themed Interface**
- Authentic terminal/hacker aesthetic with green text and dark backgrounds
- Interactive terminal command interface with custom commands
- Terminal window styling with close/minimize/maximize buttons
- Matrix-inspired color scheme and animations

### 📝 **Blog System**
- Full-featured blog with Markdown support
- SEO-optimized posts with meta descriptions and keywords
- Tag system for content organization  
- Search functionality across posts
- Reading time estimates and view counters
- RSS feed generation
- Draft/publish workflow

### 💼 **Portfolio Management**
- Showcase projects with images, descriptions, and tech stacks
- Image upload system with automatic optimization (1200x800px recommended)
- Project status tracking (Live, Development, Archived)
- Featured projects display on homepage
- External and GitHub repository links

### 🔧 **Admin Panel**
- Secure authentication system
- Content management for blog posts and portfolio items
- Contact message management
- User profile management (change username/password)
- Dashboard with site statistics
- Image upload interface for portfolio items

### 📊 **GitHub Integration**  
- Live GitHub statistics (repositories, commits, activity)
- Automatic commit counting for current month
- Repository information display
- Profile statistics integration

### 📬 **Contact System**
- Professional contact form with validation
- Email notifications for new messages
- Automatic confirmation emails to visitors
- Contact message management in admin panel

### 🔍 **SEO Optimization**
- Automatic sitemap.xml generation
- Robots.txt configuration
- Open Graph meta tags
- Twitter Card support
- JSON-LD structured data
- PWA manifest for mobile installation
- Canonical URLs and meta descriptions

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/dcblack87/terminal-portfolio.git
   cd terminal-portfolio
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux  
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python migrate.py
   ```

5. **Start the application**
   ```bash
   python run.py
   ```

6. **Access your site**
   - Visit `http://localhost:5000` to see your site
   - Login at `http://localhost:5000/login` with:
     - **Username**: `admin`
     - **Password**: `TempPassword123!`

   ⚠️ **Important**: Change the default admin credentials immediately after first login!

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Security
SECRET_KEY=your-super-secret-key-here
ADMIN_PASSWORD=your-secure-admin-password

# Site Configuration  
SITE_NAME=Your Name
SITE_TAGLINE=Your Professional Tagline
CONTACT_EMAIL=your@email.com

# GitHub Integration (Optional)
GITHUB_URL=https://github.com/yourusername
GITHUB_TOKEN=your_github_personal_access_token

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Social Media (Optional)
TWITTER_URL=https://twitter.com/yourusername
YOUTUBE_URL=https://youtube.com/@yourchannel

# Database (Production)
DATABASE_URL=postgresql://user:password@host:port/database
```

### GitHub Integration Setup

1. **Create a GitHub Personal Access Token**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` and `user` scopes
   - Add it to your `.env` file as `GITHUB_TOKEN`

2. **Update GitHub URL**
   - Set `GITHUB_URL` to your GitHub profile URL
   - The system will automatically extract your username

### Email Configuration

For Gmail users:
1. Enable 2-factor authentication
2. Generate an app-specific password
3. Use the app password in `MAIL_PASSWORD`

## 🎨 Customization

### Site Branding

Edit `app/config.py` to customize:
- Site name and tagline
- Color scheme (terminal colors)
- Contact information
- Social media links

### Content

1. **Admin Login**
   - Access `/login` with your admin credentials
   - Navigate to the admin dashboard

2. **Add Portfolio Projects**
   - Go to Portfolio → Add New Project
   - Upload images (1200x800px recommended for best display)
   - Add project details, tech stack, and links

3. **Create Blog Posts** 
   - Go to Posts → New Post
   - Write in Markdown with full formatting support
   - Add SEO meta descriptions and keywords
   - Assign tags for organization

4. **Customize About Page**
   - Edit `app/templates/main/about.html`
   - Update your bio, skills, and background

### Styling

The terminal theme can be customized in:
- `app/static/css/style.css` - Main stylesheet
- `app/config.py` - Terminal color scheme
- Individual templates for specific page styling

## 📁 Project Structure

```
terminal-portfolio/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms definitions
│   ├── email_utils.py           # Email functionality
│   ├── github_stats.py          # GitHub API integration
│   ├── image_utils.py           # Image processing
│   ├── blueprints/              # Modular route organization
│   │   ├── main/                # Main site routes
│   │   ├── blog/                # Blog functionality  
│   │   ├── auth/                # Authentication
│   │   └── admin/               # Admin panel
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template
│   │   ├── main/                # Main site pages
│   │   ├── blog/                # Blog templates
│   │   ├── admin/               # Admin panel
│   │   └── components/          # Reusable components
│   └── static/                  # CSS, JS, images
├── migrations/                  # Database migrations
├── instance/                    # Instance-specific files
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
├── migrate.py                  # Migration runner
└── README.md                   # This file
```

## 🚀 Deployment

### PythonAnywhere

1. **Upload your code**
   ```bash
   git clone https://github.com/yourusername/terminal-portfolio.git
   ```

2. **Install dependencies**
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

3. **Set environment variables**
   - In the Web tab, set environment variables
   - Add `ADMIN_PASSWORD` with a secure password

4. **Configure WSGI**
   ```python
   import sys
   path = '/home/yourusername/terminal-portfolio'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import create_app
   application = create_app()
   ```

5. **Run migrations**
   ```bash
   python migrate.py
   ```

### Heroku

1. **Create Procfile**
   ```
   web: python run.py
   ```

2. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set ADMIN_PASSWORD=your-password
   heroku config:set DATABASE_URL=postgres://...
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

## 🛠️ Development

### Adding New Features

1. **Database Changes**
   - Modify `app/models.py`
   - Create migration: `python migrate.py --specific new_feature`

2. **New Routes**
   - Add to appropriate blueprint in `app/blueprints/`
   - Update templates in `app/templates/`

3. **Styling**
   - Maintain terminal theme consistency
   - Use existing CSS classes when possible

### Running Tests

```bash
python -m pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python -m pytest`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Create Pull Request

## 📋 Features in Detail

### Terminal Interface
- Custom command processor with help system
- Real-time GitHub statistics display
- Interactive navigation commands
- Authentic terminal styling and animations

### Content Management
- WYSIWYG-style forms with validation
- Image upload with automatic optimization
- Bulk content operations in admin panel
- SEO metadata management

### Performance
- Database query optimization
- Image compression and resizing
- Caching for GitHub API calls
- Efficient pagination

### Security
- CSRF protection on all forms
- Secure password hashing (bcrypt)
- Admin-only route protection
- Input sanitization and validation

## 🤝 Support

- **Documentation**: Check this README and code comments
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Terminal aesthetic inspired by classic Unix terminals
- Flask community for excellent documentation
- GitHub API for developer statistics integration
- Open source contributors and maintainers

---

**Built with ❤️ for developers who love the terminal aesthetic**

Made something cool with this template? [Let me know!](https://www.dcblack.co.uk/contact)
