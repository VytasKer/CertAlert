# test-version-script.ps1
# Simple test to verify the version management script works

Write-Host "🧪 Testing Version Management Script" -ForegroundColor Cyan

# Test getting current version
Write-Host "`n📋 Testing current version detection..." -ForegroundColor Yellow

$testVersionFile = "VERSION.txt"
if (Test-Path $testVersionFile) {
    $currentVersion = Get-Content $testVersionFile -First 1
    Write-Host "✅ Current version detected: $currentVersion" -ForegroundColor Green
} else {
    Write-Host "❌ VERSION.txt not found" -ForegroundColor Red
}

# Test frontend .env file
$frontendEnv = "frontend\.env"
if (Test-Path $frontendEnv) {
    $envContent = Get-Content $frontendEnv
    $versionLine = $envContent | Where-Object { $_ -match "VITE_APP_VERSION=" }
    if ($versionLine) {
        $envVersion = ($versionLine -split "=")[1].Trim()
        Write-Host "✅ Frontend .env version: $envVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ VITE_APP_VERSION not found in frontend .env" -ForegroundColor Red
    }
} else {
    Write-Host "❌ frontend\.env not found" -ForegroundColor Red
}

# Test package.json
$packageJson = "frontend\package.json"
if (Test-Path $packageJson) {
    $packageContent = Get-Content $packageJson -Raw | ConvertFrom-Json
    $packageVersion = $packageContent.version
    Write-Host "✅ Package.json version: $packageVersion" -ForegroundColor Green
} else {
    Write-Host "❌ frontend\package.json not found" -ForegroundColor Red
}

Write-Host "`n🎯 Version Management Script Test Complete!" -ForegroundColor Cyan
