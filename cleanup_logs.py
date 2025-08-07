#!/usr/bin/env python3
"""
Cleanup script for contact form security logs.
Run this periodically to prevent database bloat.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.security_utils import cleanup_old_logs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Clean up old security logs."""
    app = create_app()
    
    with app.app_context():
        logger.info("Starting security log cleanup...")
        cleanup_old_logs(days_to_keep=30)
        logger.info("Cleanup completed")

if __name__ == "__main__":
    main()