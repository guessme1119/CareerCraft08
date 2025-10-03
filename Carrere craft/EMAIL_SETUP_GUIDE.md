# Email Setup Guide - OTP Email Configuration

## ✅ Steps Completed
1. ✅ Added `python-dotenv==1.0.0` to requirements.txt
2. ✅ Updated app.py to load environment variables
3. ✅ Installed python-dotenv package

## 🔧 What You Need to Do Now

### Step 1: Get Gmail App Password

1. **Enable 2-Factor Authentication** on your Gmail account (skyshotgaming08@gmail.com)
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification" if not already enabled

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Windows Computer" as the device
   - Click "Generate"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

### Step 2: Create .env File

Create a new file named `.env` in your Flask project root directory (e:\Flask\.env) with these contents:

```env
SECRET_KEY=flask-secret-key-change-this-to-something-random-and-secure-12345
MAIL_USERNAME=skyshotgaming08@gmail.com
MAIL_PASSWORD=your_16_character_app_password_here
```

**Important:**
- Replace `MAIL_PASSWORD` with the app password from Step 1
- Remove any spaces from the app password (it should be 16 characters)
- You can also change the SECRET_KEY to any random string

### Step 3: Test the Email

1. Restart your Flask application
2. Try signing up with a new email address
3. The OTP should now be sent to the email instead of appearing in the terminal

## 🔒 Security Notes

- The `.env` file is already in `.gitignore` - it won't be committed to Git
- Never share your `.env` file or commit it to version control
- Use Gmail App Passwords, not your regular Gmail password

## 🐛 Troubleshooting

**If emails still don't send:**

1. Check that your `.env` file is in the correct location (e:\Flask\.env)
2. Verify the app password has no spaces
3. Make sure 2FA is enabled on your Gmail account
4. Check the terminal for any error messages
5. Gmail might block the first email - check your Gmail security settings

**Common Errors:**

- `Authentication failed` - Wrong app password or 2FA not enabled
- `SMTPAuthenticationError` - Check your Gmail security settings
- Still showing in terminal - `.env` file not loaded or wrong credentials

## 📧 How It Works

The code in `app.py` (lines 85-126) checks if email is configured:
- If credentials are set properly → Sends email via Gmail SMTP
- If credentials are missing/default → Shows OTP in terminal (testing mode)

Once you add your real Gmail app password, it will automatically switch to sending real emails!
