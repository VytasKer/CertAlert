# reset_and_migrate_db.ps1
# PowerShell script to safely reset and migrate your SQLite database with Alembic

# Stop on error
$ErrorActionPreference = 'Stop'

# 1. Deactivate any running backend server before running this script.

# 2. Remove the old database file if it exists
if (Test-Path "backend/app/certalert.db") {
    Remove-Item "backend/app/certalert.db"
    Write-Host "Old certalert.db removed."
}

# 3. Recreate the database and run Alembic migrations
cd backend
alembic upgrade head
cd ..

Write-Host "Database reset and migrations applied."