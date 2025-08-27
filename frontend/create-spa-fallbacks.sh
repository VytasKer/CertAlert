#!/bin/bash
# Create fallback files for SPA routing

# Copy index.html to common route patterns
cp dist/index.html dist/404.html
cp dist/index.html dist/200.html

# Create directory structure for nested routes
mkdir -p dist/admin
cp dist/index.html dist/admin/index.html
cp dist/index.html dist/admin/login.html
cp dist/index.html dist/admin/dashboard.html

echo "SPA routing fallbacks created"
