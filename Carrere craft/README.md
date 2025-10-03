# Flask Role-Based Authentication with OTP Verification

A complete Flask application with role-based authentication (HR/User) and email OTP verification.

## Features

✅ **Landing Page** - Role selection (HR or User)  
✅ **Role-Based Authentication** - Separate login/signup for HR and Users  
✅ **Email OTP Verification** - 6-digit OTP sent to email during signup  
✅ **Secure Password Hashing** - Using Werkzeug  
✅ **Session Management** - Secure user sessions  
✅ **Modern UI** - Beautiful gradient design with responsive layout  
✅ **SQLite Database** - User and OTP storage  

## Project Structure

```
Flask/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── database.db            # SQLite database (auto-created)
├── templates/
│   ├── landing.html       # Role selection page
│   ├── login.html         # Login page
│   ├── signup.html        # Signup page
│   ├── verify_otp.html    # OTP verification page
│   └── dashboard.html     # User dashboard
└── README.md              # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email Settings

#### Option A: Using Gmail (Recommended)

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password:
   - Go to Security → 2-Step Verification → App passwords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

4. Create a `.env` file (copy from `.env.example`):

```env
SECRET_KEY=your-random-secret-key-here
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16_char_app_password
```

#### Option B: Using Environment Variables

Set environment variables in PowerShell:

```powershell
$env:SECRET_KEY="your-secret-key"
$env:MAIL_USERNAME="your_email@gmail.com"
$env:MAIL_PASSWORD="your_app_password"
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at: `http://127.0.0.1:5000`

## Usage Flow

### 1. Landing Page (`/`)
- Choose between HR Portal or User Portal
- Each role has separate Login and Sign Up buttons

### 2. Sign Up Process
- **Route**: `/hr/signup` or `/user/signup`
- Enter email and password
- Click "Send OTP"
- OTP is sent to your email

### 3. OTP Verification
- **Route**: `/hr/verify-otp` or `/user/verify-otp`
- Enter the 6-digit OTP from your email
- OTP expires in 10 minutes
- Option to resend OTP if needed

### 4. Login
- **Route**: `/hr/login` or `/user/login`
- Enter email and password
- Redirects to dashboard on success

### 5. Dashboard
- **Route**: `/hr/dashboard` or `/user/dashboard`
- Personalized dashboard based on role
- Logout option available

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page with role selection |
| `/<role>/login` | GET, POST | Login page |
| `/<role>/signup` | GET, POST | Signup page |
| `/<role>/verify-otp` | GET, POST | OTP verification page |
| `/<role>/resend-otp` | POST | Resend OTP |
| `/<role>/dashboard` | GET | User dashboard |
| `/logout` | GET | Logout user |

## Database Schema

### User Table
- `id` - Primary key
- `email` - Unique email address
- `password` - Hashed password
- `role` - 'hr' or 'user'
- `is_verified` - Email verification status
- `created_at` - Account creation timestamp

### OTP Table
- `id` - Primary key
- `email` - Email address
- `otp_code` - 6-digit OTP
- `created_at` - OTP creation time
- `expires_at` - OTP expiration time (10 minutes)
- `is_used` - Whether OTP has been used

## Security Features

- ✅ Password hashing with Werkzeug
- ✅ OTP expiration (10 minutes)
- ✅ One-time use OTPs
- ✅ Session-based authentication
- ✅ Role-based access control
- ✅ CSRF protection via Flask sessions

## Troubleshooting

### Email Not Sending

1. **Check Gmail App Password**: Make sure you're using an App Password, not your regular Gmail password
2. **Enable Less Secure Apps**: If not using App Password, enable "Less secure app access" in Gmail settings
3. **Check Firewall**: Ensure port 587 is not blocked
4. **Verify Credentials**: Double-check MAIL_USERNAME and MAIL_PASSWORD in .env

### OTP Not Working

1. **Check Expiration**: OTP expires in 10 minutes
2. **Case Sensitivity**: OTP is case-sensitive (numbers only)
3. **Database**: Ensure database.db is created and writable

### Login Issues

1. **Verify Email First**: Account must be verified via OTP before login
2. **Correct Role**: Make sure you're logging in with the correct role (HR/User)
3. **Password**: Passwords are case-sensitive

## Customization

### Change OTP Expiration Time

In `app.py`, modify line 55:

```python
expires_at = datetime.utcnow() + timedelta(minutes=10)  # Change 10 to desired minutes
```

### Change OTP Length

In `app.py`, modify line 50:

```python
return str(random.randint(100000, 999999))  # 6 digits
# For 4 digits: random.randint(1000, 9999)
```

### Add More Fields to Signup

1. Update the User model in `app.py`
2. Modify `signup.html` to include new fields
3. Update the signup route to handle new fields

## Tech Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLAlchemy with SQLite
- **Email**: Flask-Mail
- **Security**: Werkzeug password hashing
- **Frontend**: HTML5, CSS3 (Vanilla)

## License

MIT License - Feel free to use this project for learning or production!

## Support

For issues or questions, please create an issue in the repository.
