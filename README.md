# CertAlert - SSL Certificate Monitoring SaaS

A comprehensive certificate monitoring platform with React frontend and FastAPI backend, featuring traffic analytics, admin controls, and multi-layered security.

## Architecture Overview

### Backend (FastAPI + SQLAlchemy)
- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL (production) / SQLite (local development)
- **Authentication**: Dual-mode JWT + API key system
- **Security**: Multi-layer origin validation middleware
- **Monitoring**: Database-backed traffic analytics with IP hashing

### Frontend (React 19 + Vite)
- **Framework**: React 19 with React Router
- **Build Tool**: Vite for fast development and optimized builds
- **Deployment**: Static site with SPA fallback routing
- **Environment**: Separate configs for development and production

## Quick Start

### Development Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python run_traffic_migration.py && python create_admin_table.py
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Environment Configuration

**Root `.env` (Backend):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/certalert
SECRET_KEY=your-secret-key
ADMIN_API_KEY=your-admin-api-key
STRIPE_SECRET_KEY=sk_test_...
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@admin.com
ADMIN_PASSWORD=secure-password
DEV_MODE=true
```

**Frontend `.env`:**
```env
VITE_BACKEND_BASE_URL=http://localhost:8000
VITE_STRIPE_YEARLY_PRICE_ID=price_...
VITE_ADMIN_API_KEY=your-admin-api-key
```

## Security Architecture

### Middleware Stack (Order Critical)
1. **CORS Middleware**: Handles cross-origin requests
2. **Origin Validation**: Protects admin routes with API key validation
3. **Traffic Logging**: Captures all requests for analytics

### Authentication System
- **User Routes**: JWT token authentication (`/auth/*`, `/certificates/*`)
- **Admin Routes**: API key authentication (`/admin/*`)
- **Settings Routes**: JWT authentication (`/settings/*`)

### Admin Access
- Default admin user created on startup (ID: 99999999)
- Admin credentials configured via environment variables
- Admin routes protected by origin validation middleware

## Stripe Integration

### Payment Flow
1. Frontend displays pricing with environment-based price IDs
2. User selects plan → creates Stripe checkout session
3. Subscription record created with `INITIATED` status
4. User completes payment on Stripe
5. Webhook processes `checkout.session.completed`
6. Subscription status updated to `ACTIVATED`
7. User level promoted to `subscribed_user`

### Webhook Security
- Multiple webhook secret fallback for high availability
- All events logged regardless of processing outcome
- DEV_MODE allows unsigned webhooks for testing

## Traffic Monitoring

### Database-Only Logging
- All requests stored in `traffic_logs` table
- IP addresses hashed for privacy compliance
- JSON storage for flexible analytics queries
- Configurable retention via admin settings

### Analytics Features
- Real-time traffic statistics
- CSV exports with pagination
- Unique visitor tracking
- Response time monitoring
- Path-based analytics

## Database Management

### Migration Pattern
Uses direct SQLAlchemy table creation (not Alembic) for production reliability:

```python
# Check table existence
with engine.connect() as conn:
    result = conn.execute(text("SELECT EXISTS (...)"))
    if not result.scalar():
        ModelName.__table__.create(engine)
```

### Key Models
- **User**: Manual ID assignment, relationship with certificates
- **Certificate**: SSL certificate storage and metadata
- **Subscription**: Payment status tracking with Stripe integration
- **TrafficLog**: Analytics data with JSON storage
- **AdminSetting**: Configurable system parameters

## Production Deployment

### Render.com Configuration

**Backend Build Command:**
```bash
pip install -r requirements.txt && python create_admin_table.py
```

**Backend Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Frontend Build:**
```bash
cd frontend && npm ci && npm run build
```

### Environment Files
- Production environment variables in `.env.production`
- Frontend uses `VITE_` prefixed variables
- Backend config loading handles multiple env paths

## Admin Dashboard

### Features
- **Database Management**: Direct SQL query execution
- **Traffic Analytics**: Real-time monitoring and exports
- **System Parameters**: Configurable settings with immediate persistence
- **Log Viewing**: Application log access and download

### Access Pattern
- Login at `/admin/login` with admin credentials
- API key authentication for admin operations
- Settings changes persist immediately to database

## Development Patterns

### Error Handling
- Database operations use try/catch with rollback
- Admin settings gracefully fall back to defaults
- Frontend displays user-friendly error messages (❌, ⚠️, ✅)

### State Management
- React useState for component state
- JWT tokens stored in localStorage
- Admin settings persist to database immediately
- No separate "save" step for configuration changes

### File Organization
```
backend/
├── app/
│   ├── main.py          # Application entry point
│   ├── models.py        # Database models
│   ├── database.py      # Database configuration
│   └── [feature].py     # Feature-based modules
├── middleware/          # Request processing middleware
└── run_*.py            # Direct migration scripts

frontend/
├── src/
│   ├── pages/          # Page components
│   ├── components/     # Reusable components
│   └── hooks/          # Custom React hooks
└── public/             # Static assets
```

## Documentation

### Quick Reference
- **[Complete Documentation Index](docs/INDEX.md)** - Navigate all available documentation
- **[OAuth Implementation](docs/OAUTH_IMPLEMENTATION.md)** - Google OAuth setup and API endpoints
- **[Security Guide](docs/ORIGIN_VALIDATION_README.md)** - Middleware and route protection
- **[Version Management](docs/VERSION_GUIDE.md)** - Automated version system

### Documentation Structure
```
docs/
├── INDEX.md                        # Complete documentation navigation
├── OAUTH_IMPLEMENTATION.md         # OAuth setup and integration
├── OAUTH_ACCOUNT_LINKING.md        # Account reconciliation logic
├── ORIGIN_VALIDATION_README.md     # Security middleware guide
├── TRAFFIC_MIGRATION_README.md     # Traffic logging setup
└── VERSION_GUIDE.md                # Version management system
```

## Testing & Debugging

### Local Development
- SQLite database in project root
- DEV_MODE disables strict security checks
- Admin dashboard accessible locally
- Traffic logs visible in database

### Production Monitoring
- Traffic analytics in admin dashboard
- Error logging with comprehensive details
- Webhook event logging for payment debugging

## Key Commands

### Database Operations
```bash
# Create traffic logs table
python run_traffic_migration.py

# Create admin settings table
python create_admin_table.py

# Reset database (development only)
python recreate_all_tables.py
```

### Development
```bash
# Start backend with auto-reload
uvicorn app.main:app --reload

# Start frontend development server
npm run dev

# Build frontend for production
npm run build
```

## Configuration Reference

### Critical Environment Variables
- `DATABASE_URL`: Database connection string
- `ADMIN_API_KEY`: Admin route authentication
- `STRIPE_WEBHOOK_SECRET`: Webhook signature verification
- `DEV_MODE`: Development mode toggle
- `ENABLE_ORIGIN_VALIDATION`: Security middleware toggle

### Frontend Environment Variables
- `VITE_BACKEND_BASE_URL`: API endpoint
- `VITE_STRIPE_*_PRICE_ID`: Payment plan identifiers
- `VITE_ADMIN_API_KEY`: Admin panel authentication

---

For detailed development patterns and AI agent guidance, see `.github/copilot-instructions.md`.
