# CertAlert Documentation

This directory contains comprehensive documentation for the CertAlert certificate monitoring SaaS application.

## 📚 Documentation Index

### Core Documentation
- **[README.md](../README.md)** - Main project overview and getting started guide *(located in root)*

### Authentication & OAuth
- **[OAuth Implementation Guide](OAUTH_IMPLEMENTATION.md)** - Complete Google OAuth setup and implementation
- **[OAuth Account Linking](OAUTH_ACCOUNT_LINKING.md)** - User reconciliation and account linking logic
- **[OAuth Setup Legacy](OAUTH_SETUP_LEGACY.md)** - Legacy OAuth setup documentation

### Security & Middleware
- **[Origin Validation Guide](ORIGIN_VALIDATION_README.md)** - Middleware security and route protection

### Database & Migrations
- **[Traffic Migration Guide](TRAFFIC_MIGRATION_README.md)** - Traffic logging system setup

### Version Management
- **[Version Guide](VERSION_GUIDE.md)** - Application version management and automation

### Development Guides
- **[Copilot Instructions](../.github/copilot-instructions.md)** - AI coding agent guidance and best practices *(located in .github)*

## 🗂️ Documentation Structure

```
CertAlert/
├── README.md                          # Main project documentation
├── docs/                              # Detailed documentation
│   ├── INDEX.md                       # This file - documentation index
│   ├── OAUTH_IMPLEMENTATION.md        # OAuth setup and API endpoints
│   ├── OAUTH_ACCOUNT_LINKING.md       # Account linking and user reconciliation
│   ├── OAUTH_SETUP_LEGACY.md          # Legacy OAuth setup documentation
│   ├── ORIGIN_VALIDATION_README.md    # Security middleware documentation
│   ├── TRAFFIC_MIGRATION_README.md    # Traffic logging system setup
│   └── VERSION_GUIDE.md               # Version management automation
├── frontend/
│   └── README.md                      # Frontend-specific documentation
└── .github/
    └── copilot-instructions.md        # AI agent development guidelines
```

## 📖 Quick Navigation

### For New Developers
1. Start with **[README.md](../README.md)** for project overview
2. Review **[Copilot Instructions](../.github/copilot-instructions.md)** for development patterns
3. Check **[OAuth Implementation](OAUTH_IMPLEMENTATION.md)** for authentication setup
4. Review **[Origin Validation](ORIGIN_VALIDATION_README.md)** for security middleware

### For OAuth Implementation
1. **[OAuth Implementation Guide](OAUTH_IMPLEMENTATION.md)** - Backend setup and API endpoints
2. **[OAuth Account Linking](OAUTH_ACCOUNT_LINKING.md)** - Advanced account reconciliation

### For Database Setup
1. **[Traffic Migration Guide](TRAFFIC_MIGRATION_README.md)** - Traffic logging system
2. Check migration scripts in `/backend/run_migrations/`

### For Version Management
1. **[Version Guide](VERSION_GUIDE.md)** - Automated version management system

### For AI Development
1. **[Copilot Instructions](../.github/copilot-instructions.md)** - Security protocols and development patterns

## 🔧 Documentation Maintenance

### Adding New Documentation
- Place technical guides in `/docs/`
- Keep README.md in root for GitHub visibility
- Update this INDEX.md when adding new files
- Follow consistent markdown formatting

### Documentation Standards
- Use clear headings and sections
- Include code examples where applicable
- Provide step-by-step instructions
- Add status indicators (✅ ❌ ⚠️)
- Include troubleshooting sections

## 📝 Contributing to Documentation

When adding or updating documentation:
1. Keep technical details in `/docs/`
2. Update this index file
3. Use descriptive filenames
4. Include comprehensive examples
5. Add appropriate cross-references

---

*Last updated: September 8, 2025*
