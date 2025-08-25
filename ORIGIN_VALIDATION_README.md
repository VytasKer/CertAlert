# Origin Validation Middleware Documentation

## Overview

The Origin Validation Middleware provides security for your CertAlert API by validating request origins and implementing API key protection for administrative endpoints.

## Features

1. **Origin Header Validation** - Validates requests come from allowed domains
2. **Referer Header Fallback** - Uses referer header when origin is missing
3. **Admin API Key Protection** - Requires API key for admin routes
4. **Development Mode Support** - Flexible settings for development vs production
5. **IP Allowlist** - Allow direct API calls from development IPs
6. **Comprehensive Logging** - Track validation attempts and security events

## Configuration

### Environment Variables

Add these to your `.env` file (in the root CertAlert directory):

```env
# Origin Validation Security
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://your-production-domain.com
ADMIN_API_KEY=your-secure-api-key-here
DEV_MODE=true
ENABLE_ORIGIN_VALIDATION=true
ALLOWED_DEV_IPS=127.0.0.1,localhost,::1
STRICT_ORIGIN_VALIDATION=false
ENABLE_API_DOCS=true
PROTECT_API_DOCS=false
```

### Configuration Options

- **ALLOWED_ORIGINS**: Comma-separated list of allowed origin URLs
- **ADMIN_API_KEY**: Secure API key for admin operations (generate a strong one!)
- **DEV_MODE**: Enable/disable development mode (true/false)
- **ENABLE_ORIGIN_VALIDATION**: Master switch for the entire middleware (true/false)
- **ALLOWED_DEV_IPS**: IPs allowed to bypass origin validation in dev mode
- **STRICT_ORIGIN_VALIDATION**: Enforce strict validation even in dev mode (true/false)
- **ENABLE_API_DOCS**: Enable/disable API documentation endpoints entirely (true/false)
- **PROTECT_API_DOCS**: Require API key and origin validation for docs access (true/false)

## Usage

### Frontend API Calls

No changes needed! Your React frontend will automatically send the correct Origin headers.

### Admin Operations

For admin endpoints (like `/admin/*` or `/logs/*`), include the API key in headers:

```javascript
fetch('http://localhost:8000/admin/users', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'your-admin-api-key-here',  // Add this header
        'Authorization': 'Bearer your-jwt-token'   // Existing auth still required
    }
});
```

### Direct API Testing (Postman, curl, etc.)

In development mode (DEV_MODE=true), you can test APIs directly:

```bash
# Regular endpoint (works in dev mode from localhost)
curl http://localhost:8000/certificates

# Admin endpoint (requires API key)
curl -H "X-API-Key: your-admin-api-key-here" http://localhost:8000/admin/users
```

## Security Modes

### Development Mode (DEV_MODE=true)
- Allows direct API calls from localhost/127.0.0.1
- Less strict validation for easier testing
- More verbose logging
- Permissive when STRICT_ORIGIN_VALIDATION=false

### Production Mode (DEV_MODE=false)
- Strict origin validation required
- All requests must have valid Origin or Referer headers
- Admin routes require API keys
- Enhanced security logging

### Strict Mode (STRICT_ORIGIN_VALIDATION=true)
- Even in development, enforces origin validation
- Rejects requests without proper headers
- Use for testing production-like security

## Protected Routes

### Admin Routes (require API key):
- `/admin/*` - All admin endpoints
- `/api/admin/*` - API admin endpoints
- `/logs/*` - Log viewing endpoints
- `/api/logs/*` - Log API endpoints

### API Documentation Routes (configurable protection):
- `/docs` - Swagger UI documentation
- `/redoc` - ReDoc documentation  
- `/openapi.json` - OpenAPI schema
- **Security Options:**
  - `ENABLE_API_DOCS=false`: Completely disable docs (404 responses)
  - `PROTECT_API_DOCS=true`: Require API key and origin validation
  - `PROTECT_API_DOCS=false`: Allow unrestricted access (development only!)

### Regular Routes (origin validation only):
- All other API endpoints
- User authentication routes
- Certificate management
- Subscription handling

### Excluded Routes (no validation):
- `/health`, `/ping`, `/status` - Health checks
- Static files (.css, .js, images)

## Testing

Run the test script to verify configuration:

```bash
cd backend
python tests/test_origin_validation.py
```

This will validate:
- Configuration loading
- Origin validation logic
- IP validation
- Admin route detection

## Troubleshooting

### Common Issues

1. **"Origin not allowed" errors**
   - Check ALLOWED_ORIGINS includes your frontend URL
   - Verify no typos in URLs (http vs https, port numbers)
   - Check browser dev tools for actual Origin header value

2. **Admin routes return 401**
   - Ensure X-API-Key header is included
   - Verify API key matches ADMIN_API_KEY in .env
   - Check that route is correctly identified as admin route

3. **Development testing blocked**
   - Set DEV_MODE=true
   - Set STRICT_ORIGIN_VALIDATION=false
   - Include localhost IPs in ALLOWED_DEV_IPS

4. **CORS issues**
   - The middleware includes CORS headers in error responses
   - Check browser console for CORS-specific errors
   - Ensure existing CORS middleware is configured correctly

### Debug Mode

Enable debug logging by setting log level in your application:

```python
import logging
logging.getLogger('middleware.origin_validation').setLevel(logging.DEBUG)
```

## Production Deployment

1. **Update environment variables**:
   ```env
   ALLOWED_ORIGINS=https://your-domain.com
   DEV_MODE=false
   STRICT_ORIGIN_VALIDATION=true
   ADMIN_API_KEY=very-secure-production-key
   ENABLE_API_DOCS=false  # Disable docs entirely in production
   PROTECT_API_DOCS=true  # Or require API key if keeping docs enabled
   ```

2. **Generate secure API key**:
   ```bash
   python -c "import secrets; print('ADMIN_API_KEY=' + secrets.token_urlsafe(32))"
   ```

3. **Test thoroughly**:
   - Verify frontend works correctly
   - Test admin operations with API key
   - Confirm unauthorized requests are blocked

4. **Monitor logs**:
   - Watch for blocked requests
   - Identify any legitimate traffic being rejected
   - Monitor for suspicious activity

## Security Considerations

### What This Protects Against:
- Casual API abuse from browsers
- Simple automated scripts
- Cross-origin attacks (CSRF-like)
- Unauthorized admin access

### What This Does NOT Protect Against:
- Sophisticated attackers who can spoof headers
- Server-to-server attacks
- DDoS attacks
- Vulnerabilities in your application code

### Additional Security Recommendations:
- Use HTTPS in production
- Implement rate limiting
- Keep API keys secure and rotate regularly
- Monitor logs for suspicious patterns
- Consider additional authentication for sensitive operations

## Migration from Existing Setup

If you have existing API clients:

1. **Frontend**: No changes needed
2. **Admin tools**: Add X-API-Key header
3. **Direct API testing**: Use dev mode or add proper headers
4. **CI/CD**: Update deployment scripts with new env vars

The middleware is designed to be non-breaking for legitimate frontend usage while adding security against unauthorized access.
