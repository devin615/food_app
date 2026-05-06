# Food App - PersonalFresh

A meal planning application with Google Sign-In authentication.

## Features

- **Google Sign-In**: Secure authentication using Google OAuth 2.0
  - Sign up or log in with your existing Google account
  - No need to create a new password
  - Access your email, name, and profile picture securely
- Browse meal recipes
- Add recipes to your weekly box
- View detailed recipe information with ingredient retail links

## Prerequisites

- Python 3.7+
- A Google Cloud Project with OAuth 2.0 credentials

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install flask requests python-dotenv
```

### 2. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. Choose **Web application**
6. Set the authorized redirect URI to:
   ```
   http://localhost:5000/login/callback
   ```
7. Copy your **Client ID** and **Client Secret**

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
FLASK_SECRET_KEY=your-secure-random-key
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
FLASK_ENV=development
```

### 4. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Usage

1. Open the app in your browser
2. Click **"Sign in with Google"** button
3. Authenticate with your Google account
4. Browse recipes and add them to your box
5. Click **Logout** to sign out

## Project Structure

```
food_app/
├── app.py                 # Main Flask application
├── recipes_db.json        # Recipe database
├── .env.example          # Environment variables template
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Security Notes

- Never commit your `.env` file to version control
- Use a strong, random `FLASK_SECRET_KEY` in production
- Keep your Google OAuth credentials secure
- The app uses Flask sessions with server-side secret key
- All OAuth tokens are handled securely via HTTPS

## Google OAuth Flow

1. User clicks "Sign in with Google"
2. App redirects to Google's authorization endpoint
3. User authenticates and grants permissions
4. Google redirects back with authorization code
5. App exchanges code for access token
6. App fetches user profile information
7. User data stored in session
8. User can log out to clear session

## Dependencies

- Flask 3.1.2 - Web framework
- requests 2.32.5 - HTTP client for OAuth
- python-dotenv 1.2.2 - Environment variable management

## License

MIT