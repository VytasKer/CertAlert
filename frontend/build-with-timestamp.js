// build-with-timestamp.js
// Script to inject build timestamp into environment variables

import { writeFileSync, readFileSync } from 'fs';
import { join } from 'path';

const buildDate = new Date().toISOString();
const envFile = '.env';

// Read current .env file
let envContent = '';
try {
  envContent = readFileSync(envFile, 'utf8');
} catch (error) {
  console.log('No .env file found, creating new one');
}

// Remove existing build date if present
envContent = envContent.replace(/^VITE_BUILD_DATE=.*$/m, '');

// Add new build date
envContent += `\nVITE_BUILD_DATE=${buildDate}\n`;

// Write back to .env file
writeFileSync(envFile, envContent.trim() + '\n');

console.log(`✅ Build timestamp added: ${buildDate}`);
console.log(`📝 Updated ${envFile}`);

export default buildDate;
