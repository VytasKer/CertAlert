# Google OAuth Setup Guide

## Overview
This guide explains how to set up Google OAuth integration for CertAlert application.

## Google Cloud Console Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name it something like "CertAlert OAuth"

### 2. Enable Google+ API
1. Go to "APIs & Services" > "Library"
2. Search for "Google+ API" 
3. Click "Enable"

### 3. Configure OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in required fields:
   - App name: "CertAlert"
   - User support email: your email
   - Developer contact information: your email
4. Add scopes:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`
5. Save and continue

### 4. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Configure:
   - Name: "CertAlert Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:5173` (development)
     - `https://certalert.onrender.com` (production)
   - Authorized redirect URIs:
     - `http://localhost:5173/oauth/google/callback` (development)
     - `https://certalert.onrender.com/oauth/google/callback` (production)
5. Save and download credentials

## Environment Configuration

### Development (.env)
```bash
GOOGLE_CLIENT_ID=your_actual_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5173/oauth/google/callback
```

### Production (.env.production)
```bash
GOOGLE_CLIENT_ID=your_production_client_id_here
GOOGLE_CLIENT_SECRET=your_production_client_secret_here
GOOGLE_REDIRECT_URI=https://certalert.onrender.com/oauth/google/callback
```

## API Endpoints

### Backend OAuth Endpoints
- `GET /oauth/google/login` - Get Google authorization URL
- `GET /oauth/google/callback` - Handle OAuth callback
- `POST /oauth/google/link-account` - Link Google to existing account (future)
- `DELETE /oauth/google/unlink` - Unlink Google account (future)

### OAuth Flow
1. Frontend calls `/oauth/google/login` to get authorization URL
2. User is redirected to Google for authentication
3. Google redirects back to frontend callback URL with code
4. Frontend sends code to `/oauth/google/callback`
5. Backend exchanges code for user info and returns JWT token

## Database Schema
OAuth adds these fields to User model:
- `google_id` - Google user ID
- `google_email` - Google email (may differ from primary email)
- `profile_picture_url` - Google profile picture URL
- `auth_provider` - 'local' or 'google'
- `email_verified` - Boolean (Google users are pre-verified)
- `last_google_sync` - Last sync timestamp

## Testing
Run the OAuth test script:
```bash
cd backend
python test_oauth.py
```

## Security Considerations
- OAuth credentials are sensitive - never commit to git
- Use HTTPS in production
- Validate state parameter for CSRF protection
- JWT tokens expire in 15 minutes (configurable)
- Google users get dummy password hash (cannot use password login)

## Troubleshooting

### Common Issues
1. **"redirect_uri_mismatch"** - Check OAuth redirect URIs in Google Console
2. **"invalid_client"** - Verify client ID and secret
3. **"access_denied"** - User declined authorization
4. **Database errors** - Run OAuth migration first

### Debugging
- Check `/docs` for API documentation
- Monitor backend logs for OAuth errors
- Use test script to verify setup
- Verify environment variables are loaded
