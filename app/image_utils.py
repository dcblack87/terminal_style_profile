"""
Image processing utilities for portfolio uploads.

Handles image resizing, optimization, and file management for portfolio items.
Recommended portfolio image size: 1200x800px (3:2 aspect ratio) for best display.
"""

import os
import uuid
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
from flask import current_app

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Optimal portfolio image dimensions
PORTFOLIO_IMAGE_WIDTH = 1200
PORTFOLIO_IMAGE_HEIGHT = 800

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts."""
    # Get file extension
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    
    # Generate unique filename with UUID
    unique_filename = f"portfolio_{uuid.uuid4().hex[:12]}.{ext}"
    return unique_filename

def resize_and_optimize_image(image_path, max_width=PORTFOLIO_IMAGE_WIDTH, max_height=PORTFOLIO_IMAGE_HEIGHT, quality=85):
    """
    Resize and optimize an image for portfolio display.
    
    Args:
        image_path (str): Path to the image file
        max_width (int): Maximum width in pixels
        max_height (int): Maximum height in pixels
        quality (int): JPEG quality (1-100)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (handles RGBA, P mode images)
            if img.mode in ('RGBA', 'P'):
                # Create a white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Calculate new dimensions maintaining aspect ratio
            original_width, original_height = img.size
            
            # Calculate ratios
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            
            # Use the smaller ratio to ensure image fits within bounds
            ratio = min(width_ratio, height_ratio)
            
            # Only resize if image is larger than target
            if ratio < 1:
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                # Use LANCZOS for high-quality resizing
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
            return True
            
    except Exception as e:
        current_app.logger.error(f"Image processing failed: {str(e)}")
        return False

def save_portfolio_image(uploaded_file):
    """
    Save and process an uploaded portfolio image.
    
    Args:
        uploaded_file: Flask uploaded file object
        
    Returns:
        tuple: (success: bool, filename: str, error_message: str)
    """
    if not uploaded_file or uploaded_file.filename == '':
        return False, None, "No file selected"
    
    if not allowed_file(uploaded_file.filename):
        return False, None, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    try:
        # Generate unique filename
        filename = generate_unique_filename(uploaded_file.filename)
        
        # Ensure upload directory exists
        upload_path = os.path.join(current_app.root_path, 'static', 'images', 'portfolio')
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, filename)
        uploaded_file.save(file_path)
        
        # Process and optimize image
        if resize_and_optimize_image(file_path):
            return True, filename, None
        else:
            # Remove file if processing failed
            try:
                os.remove(file_path)
            except:
                pass
            return False, None, "Image processing failed"
            
    except Exception as e:
        current_app.logger.error(f"File upload failed: {str(e)}")
        return False, None, f"Upload failed: {str(e)}"

def delete_portfolio_image(filename):
    """
    Delete a portfolio image file.
    
    Args:
        filename (str): Name of the file to delete
        
    Returns:
        bool: True if successful or file doesn't exist, False on error
    """
    if not filename:
        return True
        
    try:
        file_path = os.path.join(current_app.root_path, 'static', 'images', 'portfolio', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to delete image {filename}: {str(e)}")
        return False

def get_portfolio_image_url(filename):
    """
    Get the URL for a portfolio image.
    
    Args:
        filename (str): Image filename
        
    Returns:
        str: URL to the image or None if no filename
    """
    if not filename:
        return None
    
    return f"/static/images/portfolio/{filename}"

def get_image_info(filename):
    """
    Get information about an uploaded image.
    
    Args:
        filename (str): Image filename
        
    Returns:
        dict: Image information or None if file doesn't exist
    """
    if not filename:
        return None
        
    try:
        file_path = os.path.join(current_app.root_path, 'static', 'images', 'portfolio', filename)
        if not os.path.exists(file_path):
            return None
            
        with Image.open(file_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': os.path.getsize(file_path)
            }
    except Exception:
        return None