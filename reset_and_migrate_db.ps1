# reset_and_migrate_db.ps1
# PowerShell script to reset and migrate your PostgreSQL database with Alembic

# Stop on error
$ErrorActionPreference = 'Stop'

Write-Host "🚨 WARNING: This will reset your PostgreSQL database!" -ForegroundColor Red
Write-Host "Make sure you have a backup if needed." -ForegroundColor Yellow
$confirmation = Read-Host "Type 'RESET' to continue"

if ($confirmation -ne "RESET") {
    Write-Host "Operation cancelled." -ForegroundColor Green
    exit
}

# 1. Deactivate any running backend server before running this script.

Write-Host "🔄 Resetting PostgreSQL database..." -ForegroundColor Blue

# 2. Navigate to backend directory
Set-Location backend

# 3. Drop all tables and recreate with Alembic
Write-Host "📝 Running Alembic migrations..." -ForegroundColor Blue
alembic upgrade head

Set-Location ..

Write-Host "✅ Database reset and migrations applied successfully!" -ForegroundColor Green