# Gmail Setup for OTP Email

## ⚠️ IMPORTANT: Your current password won't work!

Gmail requires an **App Password** for third-party apps, not your regular Gmail password.

## Steps to Generate Gmail App Password:

### 1. Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Click on **2-Step Verification**
3. Follow the steps to enable it (if not already enabled)

### 2. Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select **Mail** as the app
3. Select **Windows Computer** as the device
4. Click **Generate**
5. Copy the **16-character password** (it will look like: `abcd efgh ijkl mnop`)

### 3. Update app.py

Replace line 19 in `app.py`:

```python
# OLD (won't work):
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '@skyshot08')

# NEW (use the 16-character app password):
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'abcdefghijklmnop')
```

**Remove the spaces from the app password!**

## Alternative: Use Environment Variables (Recommended)

Instead of hardcoding in the file, set environment variables in PowerShell:

```powershell
$env:MAIL_USERNAME="skyshotgaming08@gmail.com"
$env:MAIL_PASSWORD="your_16_char_app_password_here"
```

Then run:
```powershell
python app.py
```

## Quick Test (Without Email)

If you want to test without setting up email, the app will automatically show OTP in the console/terminal when you sign up!

Just look for output like:
```
============================================================
📧 EMAIL NOT CONFIGURED - SHOWING OTP IN CONSOLE
============================================================
Email: test@example.com
OTP Code: 123456
This OTP will expire in 10 minutes
============================================================
```
