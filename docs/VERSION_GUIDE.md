# CertAlert Version Management Guide

## Quick Version Update

### Using the PowerShell Script (Recommended)
```powershell
# Increment patch version (0.0.9 -> 0.0.10)
.\update-version.ps1 -Type patch

# Increment minor version (0.0.9 -> 0.1.0)
.\update-version.ps1 -Type minor

# Increment major version (0.0.9 -> 1.0.0)
.\update-version.ps1 -Type major

# Set alpha/beta/rc suffix
.\update-version.ps1 -Type alpha
.\update-version.ps1 -Type beta
.\update-version.ps1 -Type rc

# Set custom version
.\update-version.ps1 -CustomVersion "1.0.0-beta.2"
```

**✅ Status**: Script fixed and working properly (September 8, 2025)
- Fixed PowerShell syntax errors with quotes and encoding
- Removed problematic emoji characters for better compatibility
- All version files now update correctly

### Manual Update
1. Edit `VERSION.txt` in project root
2. Update `VITE_APP_VERSION` in both `frontend/.env` and `frontend/.env.production`
3. Update `version` field in `frontend/package.json`

## Version Display

### Admin Dashboard
The version is displayed in the Admin Dashboard under "Application Information" with:
- ✅ Version number with color-coded badges
- ✅ Environment indicator (development/production)
- ✅ Build timestamp
- ✅ Version type notes (alpha/beta/rc/release)

### Environment Variables
- `VITE_APP_VERSION`: Current application version
- `VITE_BUILD_DATE`: Automatically set during build process

## Version Semantics

### Version Format: `MAJOR.MINOR.PATCH[-SUFFIX]`
- **MAJOR**: Breaking changes, new architecture
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, small improvements
- **SUFFIX**: 
  - `alpha`: Early development, may have bugs
  - `beta`: Feature-complete, testing phase
  - `rc`: Release candidate, nearly production ready

### Recommended Workflow
1. **Development**: Use `-alpha` suffix
2. **Feature Testing**: Use `-beta` suffix  
3. **Pre-production**: Use `-rc` suffix
4. **Production**: Remove suffix (stable release)

## Build Process

### Development Build
```bash
cd frontend
npm run dev
```

### Production Build
```bash
cd frontend
npm run build:production
```
This automatically:
- ✅ Checks current version
- ✅ Adds build timestamp
- ✅ Builds optimized bundle
- ✅ Creates SPA fallbacks

## File Locations

- `VERSION.txt` - Master version file with history
- `frontend/.env` - Development environment variables
- `frontend/.env.production` - Production environment variables
- `frontend/package.json` - Package version (should match)
- `frontend/src/pages/AdminDashboard.jsx` - Version display component

## Git Integration

### Commit Pattern
```bash
# After version update
git add .
git commit -m "Bump version to v1.0.0-beta"
git tag "v1.0.0-beta"
git push origin main --tags
```

### Release Notes Template
```markdown
## Version 1.0.0-beta (2025-09-08)

### New Features
- Feature 1
- Feature 2

### Bug Fixes  
- Fix 1
- Fix 2

### Breaking Changes
- Change 1
```

## Automation Ideas (Future)

1. **GitHub Actions**: Automatic version bumping on PR merge
2. **Pre-commit hooks**: Ensure version consistency
3. **Changelog generation**: Automatic release notes
4. **Deployment triggers**: Deploy on version tag

## Troubleshooting

### Version Mismatch
If versions are inconsistent across files:
```powershell
.\update-version.ps1 -CustomVersion "0.0.9-alpha"
```

### Missing Build Date
Build timestamp is added automatically during `npm run build`. If missing:
```bash
node build-with-timestamp.js
```
