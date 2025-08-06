# Google reCAPTCHA Setup Guide

## Overview
Google reCAPTCHA has been successfully integrated into your contact form. To complete the setup, you need to obtain API keys from Google and configure environment variables.

## Steps to Complete Setup

### 1. Get Google reCAPTCHA Keys
1. Go to [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin/create)
2. Click "Create" to add a new site
3. Fill in the form:
   - **Label**: Your site name (e.g., "dcblack.co.uk Contact Form")
   - **reCAPTCHA type**: Choose "reCAPTCHA v2" → "I'm not a robot" checkbox
   - **Domains**: Add your domain(s):
     - `dcblack.co.uk`
     - `www.dcblack.co.uk`
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

## What's Been Implemented

### ✅ Code Changes Made:
1. **Dependencies**: Updated requirements.txt with proper Flask-WTF dependency
2. **Configuration**: Added reCAPTCHA config settings to `app/config.py`
3. **Form**: Added reCAPTCHA field to `ContactForm` in `app/forms.py`
4. **Template**: Added reCAPTCHA widget to contact form in `app/templates/main/contact.html`
5. **Styling**: Added terminal-themed CSS for reCAPTCHA in `app/static/src/style.css`
6. **Validation**: Automatic validation through existing form handling

### 🔧 Features:
- **Security**: Protects against spam and bot submissions
- **User Experience**: Clean integration with terminal theme
- **Error Handling**: Shows validation errors if reCAPTCHA fails
- **Responsive**: Works on all device sizes

## Testing

### Before Going Live:
1. Set up reCAPTCHA keys as described above
2. Test the contact form locally
3. Verify reCAPTCHA appears and functions correctly
4. Test form submission with and without completing reCAPTCHA
5. Check that validation errors display properly

### Troubleshooting:
- **reCAPTCHA not appearing**: Check that `RECAPTCHA_PUBLIC_KEY` is set correctly
- **Validation always fails**: Verify `RECAPTCHA_PRIVATE_KEY` is correct
- **Domain errors**: Ensure your domain is added to the reCAPTCHA site configuration

## Security Notes
- Never commit your secret key to version control
- Use different keys for development and production if needed
- Regularly monitor your reCAPTCHA admin console for suspicious activity

---

Your contact form now has enterprise-grade spam protection while maintaining the sleek terminal aesthetic! 🛡️