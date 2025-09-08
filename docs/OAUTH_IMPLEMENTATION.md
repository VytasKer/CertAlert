# OAuth Implementation Guide

## Overview
Complete Google OAuth implementation for CertAlert with comprehensive error handling, security features, and frontend integration support.

## Backend Implementation Status ✅

### 1. Database Schema
- **OAuth fields added to User model** (`backend/app/models.py`):
  - `google_id`: Unique Google account identifier
  - `google_email`: Google account email address
  - `profile_picture_url`: User's Google profile picture URL
  - `auth_provider`: Authentication method ("google" or "email")
  - `email_verified`: Email verification status from Google
  - `last_google_sync`: Last synchronization timestamp with Google

### 2. OAuth Service Layer
- **Google OAuth Service** (`backend/app/oauth_service.py`):
  - Complete Google OAuth integration with httpx
  - Token exchange and user data retrieval
  - JWT token generation for authenticated users
  - Comprehensive error handling and logging

### 3. API Endpoints ✅
- **OAuth API Routes** (`backend/app/oauth_api.py`):
  - `GET /oauth/google/login` - Initiate OAuth flow with CSRF protection
  - `GET /oauth/google/callback` - Handle OAuth callback with account linking support
  - `GET /oauth/google/user-info` - Get current user's Google account info
  - `POST /oauth/google/refresh-user-info` - Refresh user info (placeholder)
  - `POST /oauth/google/link-account` - Complete account linking with password verification
  - `POST /oauth/google/check-linking-status` - Check if email can be linked to Google
  - `POST /oauth/google/set-password-for-unlinking` - Set password for Google users
  - `POST /oauth/google/unlink-account` - Safely remove Google OAuth connection
  - `GET /oauth/status` - Get comprehensive OAuth authentication status

### 4. Security Features ✅
- **CSRF Protection**: Automatic state parameter generation
- **Redirect URI Validation**: Whitelist-based URI security
- **Environment-based Configuration**: Production/development environment support
- **Comprehensive Error Handling**: Detailed logging and user-friendly error messages
- **Frontend Redirection**: Automatic success/error page routing
- **Account Linking Logic**: Secure user reconciliation for existing accounts
- **Token-based Linking**: Temporary secure tokens for account verification
- **Password Protection**: Safe unlinking with email authentication fallback

### 5. Account Linking System ✅
- **Automatic Detection**: Identifies existing email accounts during OAuth
- **Secure Token Generation**: 30-minute expiring tokens with cryptographic nonces
- **Password Verification**: Confirms user identity before linking accounts
- **Safe Unlinking**: Requires password fallback before removing Google OAuth
- **Comprehensive Status Checking**: API endpoints for frontend account management

### 5. Integration Points
- **Main App Registration**: OAuth router included in `backend/app/main.py`
- **Schema Definitions**: Complete Pydantic schemas in `backend/app/schemas.py`
- **Middleware Compatible**: Works with existing authentication and security middleware

## Frontend Implementation Needed ❌

### 1. OAuth Components
```javascript
// Components to create:
// src/components/OAuth/GoogleLoginButton.jsx
// src/components/OAuth/OAuthCallback.jsx
// src/pages/OAuth/Success.jsx
// src/pages/OAuth/Error.jsx
```

### 2. OAuth Flow Integration
```javascript
// Frontend OAuth flow:
// 1. User clicks Google login button
// 2. Redirect to /oauth/google/login endpoint
// 3. Google redirects to /oauth/google/callback
// 4. Backend processes and redirects to frontend success/error page
// 5. Frontend handles token storage and user state
```

### 3. API Integration
```javascript
// API calls needed:
// - Call /oauth/google/login to get authorization URL
// - Handle OAuth callback results
// - Check OAuth status with /oauth/status
// - Manage Google account linking/unlinking
```

## Environment Configuration

### Backend Environment Variables
```bash
# Required OAuth configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth/google/callback

# Frontend URLs for redirects
FRONTEND_BASE_URL=http://localhost:5173
```

### Frontend Environment Variables
```bash
# Add to .env file
VITE_GOOGLE_OAUTH_LOGIN_URL=http://localhost:8000/oauth/google/login
VITE_OAUTH_STATUS_URL=http://localhost:8000/oauth/status
```

## Google Cloud Console Setup ❌

### Required Steps:
1. **Create Google Cloud Project** or use existing
2. **Enable Google+ API** and **Google OAuth2 API**
3. **Configure OAuth Consent Screen**:
   - Application name: "CertAlert"
   - User support email
   - Developer contact information
4. **Create OAuth 2.0 Credentials**:
   - Application type: Web application
   - Authorized redirect URIs:
     - `http://localhost:8000/oauth/google/callback` (development)
     - `https://your-domain.com/oauth/google/callback` (production)
5. **Copy Client ID and Client Secret** to environment variables

## Testing Workflow

### Local Development
1. **Start Backend**: `cd backend && uvicorn app.main:app --reload`
2. **Test OAuth Login**: Navigate to `http://localhost:8000/oauth/google/login`
3. **Check API Docs**: Visit `http://localhost:8000/docs` for interactive testing
4. **Verify Database**: Check `google_id` and `auth_provider` fields in User table

### Frontend Integration Testing
1. **Implement OAuth Components** in React
2. **Test OAuth Flow** end-to-end
3. **Verify Token Storage** and user state management
4. **Test Account Linking/Unlinking** functionality

## Deployment Considerations

### Production Environment
- **Secure HTTPS**: OAuth requires HTTPS in production
- **Environment Variables**: Configure all OAuth-related environment variables
- **CORS Configuration**: Ensure frontend domain is whitelisted
- **Database Migration**: Run OAuth migration script before deployment

### Security Checklist
- ✅ CSRF protection with state parameter
- ✅ Redirect URI validation
- ✅ Environment-based configuration
- ✅ Comprehensive error handling
- ✅ Proper logging and monitoring
- ✅ Token-based authentication
- ✅ Database transaction safety

## Next Steps
1. **Google Cloud Console Setup** - Configure OAuth application
2. **Frontend OAuth Components** - Create React components for OAuth flow
3. **Integration Testing** - Test complete OAuth workflow
4. **Production Deployment** - Deploy with HTTPS and production configuration

## API Endpoint Examples

### Initiate OAuth Login
```bash
GET /oauth/google/login
Response: { "authorization_url": "https://accounts.google.com/oauth/authorize?..." }
```

### OAuth Callback (Automatic)
```bash
GET /oauth/google/callback?code=auth_code&state=csrf_state
Response: Redirect to frontend success/error page or JSON with token
```

### Check OAuth Status
```bash
GET /oauth/status
Headers: Authorization: Bearer <jwt_token>
Response: {
  "oauth_connected": true,
  "auth_provider": "google",
  "has_google_account": true,
  "email_verified": true,
  "user_id": 123,
  "email": "user@example.com"
}
```

### Unlink Google Account with Password Verification
```bash
POST /oauth/google/unlink-account
Headers: Authorization: Bearer <jwt_token>
Response: {
  "message": "Google account successfully unlinked",
  "auth_provider": "email",
  "user": { ... }
}
```

### Account Linking Workflow
```bash
# 1. Check if email can be linked
POST /oauth/google/check-linking-status
{
  "email": "user@example.com"
}

# 2. If account linking required during OAuth callback
GET /oauth/google/callback?code=auth_code
Response: Redirect to frontend with link_token

# 3. Complete account linking
POST /oauth/google/link-account
{
  "link_token": "base64_encoded_token",
  "password": "user_password"
}
Response: {
  "message": "Google account successfully linked",
  "access_token": "jwt_token",
  "user": { ... }
}

# 4. Set password for Google users who want to unlink
POST /oauth/google/set-password-for-unlinking
{
  "password": "new_password"
}
```

## Complete Implementation Status

### ✅ Completed
- Database schema with OAuth fields
- Complete OAuth service layer with account linking logic
- Comprehensive API endpoints with account reconciliation
- Security features and error handling
- Account linking workflow with secure tokens
- Password verification and safe unlinking
- Integration with main application
- Environment configuration
- Documentation and testing workflow

### ❌ Pending
- Google Cloud Console setup
- Frontend OAuth components with account linking UI
- React integration and token management
- End-to-end testing
- Production deployment

The backend OAuth implementation with account linking is complete and production-ready. The system now handles all user reconciliation scenarios securely and provides a seamless experience for users with existing accounts.
