#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get current directory in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create the dist directory if it doesn't exist
const distDir = path.join(__dirname, 'dist');

// Read the main index.html
const indexHtmlPath = path.join(distDir, 'index.html');
const indexHtmlContent = fs.readFileSync(indexHtmlPath, 'utf8');

// Create fallback files
fs.writeFileSync(path.join(distDir, '404.html'), indexHtmlContent);
fs.writeFileSync(path.join(distDir, '200.html'), indexHtmlContent);

// Create directory structure and fallback files for nested routes
const routes = ['admin', 'dashboard', 'profile'];

routes.forEach(route => {
    const routeDir = path.join(distDir, route);
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(routeDir)) {
        fs.mkdirSync(routeDir, { recursive: true });
    }
    
    // Copy index.html to the route directory
    fs.writeFileSync(path.join(routeDir, 'index.html'), indexHtmlContent);
});

console.log('SPA fallback files created successfully!');
