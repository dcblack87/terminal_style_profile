# Google reCAPTCHA Setup Guide

## Overview
Google reCAPTCHA has been successfully integrated into the contact form. To complete the setup, you need to obtain API keys from Google and configure environment variables.

## Steps to Complete Setup

### 1. Get Google reCAPTCHA Keys
1. Go to [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin/create)
2. Click "Create" to add a new site
3. Fill in the form:
   - **Label**: Your site name (e.g., "dcblack.co.uk Contact Form")
   - **reCAPTCHA type**: Choose "reCAPTCHA v2" → "I'm not a robot" checkbox
   - **Domains**: Add your domain(s):
     - `yoursite.com`
     - `www.yoursite.com`
     - `localhost` (for development)
     - `127.0.0.1` (for development)
4. Accept the Terms of Service
5. Click "Submit"

### 2. Configure Environment Variables
Add the following environment variables to your system or `.env` file:

```bash
# Google reCAPTCHA Configuration
RECAPTCHA_PUBLIC_KEY=your_site_key_here
RECAPTCHA_PRIVATE_KEY=your_secret_key_here
```

**Important**: 
- The **Site Key** goes in `RECAPTCHA_PUBLIC_KEY`
- The **Secret Key** goes in `RECAPTCHA_PRIVATE_KEY`

### 3. For Development
If you're using a `.env` file for development, create one in your project root:

```bash
# .env file
RECAPTCHA_PUBLIC_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_PRIVATE_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 4. For Production
Set these environment variables on your production server:
- Through your hosting provider's control panel
- Or via command line: `export RECAPTCHA_PUBLIC_KEY=your_key_here`
