# OAuth Configuration Guide for CertAlert

## 📁 **File Structure Overview**

CertAlert uses **two separate `.env` files**:

### **Backend Configuration** (Root Directory)
- **File**: `/.env` (root of project)
- **Purpose**: Backend settings (OAuth, database, SMTP, Stripe)
- **Used by**: FastAPI backend server

### **Frontend Configuration** (Frontend Directory)  
- **File**: `/frontend/.env`
- **Purpose**: Frontend settings (all variables prefixed with `VITE_`)
- **Used by**: React frontend with Vite

---

## 🔧 **Google OAuth Setup**

### **Step 1: Google Cloud Console Setup**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a New Project** (or select existing):
   - Project name: "CertAlert"
   - Click "Create"

3. **Enable Google APIs**:
   - Go to "APIs & Services" → "Library"
   - Search and enable:
     - "Google+ API"
     - "Google Identity Services API"

4. **Configure OAuth Consent Screen**:
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" (for testing)
   - Fill required fields:
     - App name: "CertAlert"
     - User support email: your email
     - Developer contact: your email
   - Save and continue through all steps

5. **Create OAuth 2.0 Client**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Name: "CertAlert OAuth Client"

6. **Configure Authorized URIs**:
   
   **Authorized JavaScript origins:**
   ```
   http://localhost:5173
   http://localhost:3000
   ```
   
   **Authorized redirect URIs:**
   ```
   http://localhost:5173/oauth/success
   http://localhost:5173/oauth/error
   http://localhost:5173/oauth/link-account
   http://localhost:8000/oauth/google/callback
   ```

7. **Get Your Credentials**:
   - Copy the **Client ID** and **Client Secret**

---

## ⚙️ **Configuration Files**

### **Backend Configuration** (`/.env`)

Add these lines to your **root `.env` file**:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=123456789-abcdefghijk.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-secret-here
GOOGLE_REDIRECT_URI=http://localhost:5173/oauth/google/callback
```

**⚠️ Important**: 
- Replace with your **actual credentials** from Google Cloud Console
- Keep the `GOOGLE_REDIRECT_URI` exactly as shown
- Never commit real credentials to version control

### **Frontend Configuration** (`/frontend/.env`)

Your frontend `.env` is already configured correctly:

```bash
# OAuth configuration (already set)
VITE_OAUTH_LOGIN_URL=http://localhost:8000/oauth/google/login
VITE_OAUTH_STATUS_URL=http://localhost:8000/oauth/status
VITE_OAUTH_UNLINK_URL=http://localhost:8000/oauth/google/unlink-account
```

---

## 🧪 **Testing OAuth Setup**

### **Step 1: Update Backend Configuration**

1. **Edit root `.env` file** and replace:
   ```bash
   GOOGLE_CLIENT_ID=your_actual_client_id_here
   GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
   ```

2. **Restart backend server** to load new environment variables

### **Step 2: Test OAuth Flow**

1. **Start both servers**:
   ```bash
   # Backend (from root directory)
   cd backend
   python -m uvicorn app.main:app --reload
   
   # Frontend (from root directory)  
   cd frontend
   npm run dev
   ```

2. **Test OAuth**:
   - Go to: http://localhost:5173
   - Navigate to Profile → Account Connections
   - Click "Link Google Account"
   - Should redirect to Google sign-in (not show placeholder URL)

### **Step 3: Verify Success**

✅ **Success indicators**:
- Redirects to real Google sign-in page
- No "your_google_client_id_here" in URL
- Can complete OAuth flow and return to app

❌ **Still showing placeholder**:
- Check root `.env` file has correct values
- Restart backend server after changes
- Verify no extra spaces or quotes in `.env` values

---

## 🔐 **Security Notes**

### **Environment Variables**
- **Root `.env`**: Contains sensitive backend secrets (OAuth, database, SMTP)
- **Frontend `.env`**: Contains public configuration (URLs, public keys)
- Both files are in `.gitignore` and should never be committed

### **Production Setup**
- Use environment-specific credential sets
- Enable HTTPS for OAuth redirects
- Restrict OAuth redirect URIs to your domain
- Use separate Google Cloud projects for dev/prod

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **"your_google_client_id_here" still showing**:
   - Credentials are in wrong file (should be root `.env`, not frontend)
   - Backend server not restarted after changes
   - Typo in environment variable names

2. **"Redirect URI mismatch" error**:
   - Add all redirect URIs to Google Cloud Console
   - Check for http vs https mismatch
   - Verify port numbers match

3. **OAuth callback fails**:
   - Backend server not running on port 8000
   - CORS issues (check `ALLOWED_ORIGINS` in root `.env`)
   - Firewall blocking requests

### **Debug Commands**

Check if credentials are loaded:
```bash
cd backend
python -c "import os; print('Client ID:', os.getenv('GOOGLE_CLIENT_ID', 'NOT SET'))"
```

Verify backend endpoints:
```bash
curl http://localhost:8000/oauth/google/login
```

---

## 📋 **Quick Checklist**

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured  
- [ ] OAuth 2.0 client created
- [ ] Redirect URIs added to Google Cloud Console
- [ ] Credentials added to **root `.env`** file
- [ ] Backend server restarted
- [ ] OAuth flow tested end-to-end

Once configured, users can link their Google accounts through the Profile → Account Connections tab! 🎉
