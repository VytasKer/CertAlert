# Version Management Script for CertAlert
# PowerShell script to manage version across frontend and backend

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("patch", "minor", "major", "alpha", "beta", "rc")]
    [string]$Type = "patch",

    [Parameter(Mandatory=$false)]
    [string]$CustomVersion = ""
)

# Get current directory
$ProjectRoot = Get-Location

# Define version files
$FrontendEnvDev = "$ProjectRoot\frontend\.env"
$FrontendEnvProd = "$ProjectRoot\frontend\.env.production"
$FrontendPackageJson = "$ProjectRoot\frontend\package.json"
$VersionInfo = "$ProjectRoot\VERSION.txt"

function Get-CurrentVersion {
    if (Test-Path $VersionInfo) {
        return Get-Content $VersionInfo -First 1
    }

    # Fallback to frontend .env file
    if (Test-Path $FrontendEnvDev) {
        $content = Get-Content $FrontendEnvDev
        $versionLine = $content | Where-Object { $_ -match "VITE_APP_VERSION=" }
        if ($versionLine) {
            return ($versionLine -split "=")[1].Trim()
        }
    }

    return "0.0.9-alpha"
}

function New-Version {
    param($CurrentVersion, $Type)

    # Parse current version (e.g., "0.0.9-alpha" -> major=0, minor=0, patch=9, suffix=alpha)
    if ($CurrentVersion -match "^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = [int]$matches[3]
        $suffix = $matches[4]
    } else {
        Write-Error "Invalid version format: $CurrentVersion"
        return $CurrentVersion
    }

    switch ($Type) {
        "major" {
            $major++; $minor = 0; $patch = 0; $suffix = $null
        }
        "minor" {
            $minor++; $patch = 0; $suffix = $null
        }
        "patch" {
            $patch++; $suffix = $null
        }
        "alpha" {
            $suffix = "alpha"
        }
        "beta" {
            $suffix = "beta"
        }
        "rc" {
            $suffix = "rc"
        }
    }

    if ($suffix) {
        return "$major.$minor.$patch-$suffix"
    } else {
        return "$major.$minor.$patch"
    }
}

function Update-VersionInFile {
    param($FilePath, $NewVersion, $Pattern, $Replacement)

    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath
        $updatedContent = $content -replace $Pattern, $Replacement
        Set-Content -Path $FilePath -Value $updatedContent
        Write-Host "Updated version in $FilePath" -ForegroundColor Green
    } else {
        Write-Warning "File not found: $FilePath"
    }
}

# Main execution
Write-Host "CertAlert Version Manager" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

$currentVersion = Get-CurrentVersion
Write-Host "Current version: $currentVersion" -ForegroundColor Yellow

if ($CustomVersion) {
    $newVersion = $CustomVersion
    Write-Host "Setting custom version: $newVersion" -ForegroundColor Blue
} else {
    $newVersion = New-Version -CurrentVersion $currentVersion -Type $Type
    Write-Host "New version ($Type): $newVersion" -ForegroundColor Blue
}

# Confirm with user
$confirmation = Read-Host "Continue with version update? (y/N)"
if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host "Version update cancelled" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Updating version files..." -ForegroundColor Cyan

# Update VERSION.txt
$buildDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Set-Content -Path $VersionInfo -Value @(
    $newVersion,
    "Updated: $buildDate",
    "Type: $Type",
    "Previous: $currentVersion"
)
Write-Host "Updated $VersionInfo" -ForegroundColor Green

# Update frontend .env files
Update-VersionInFile -FilePath $FrontendEnvDev -NewVersion $newVersion -Pattern "VITE_APP_VERSION=.*" -Replacement "VITE_APP_VERSION=$newVersion"
Update-VersionInFile -FilePath $FrontendEnvProd -NewVersion $newVersion -Pattern "VITE_APP_VERSION=.*" -Replacement "VITE_APP_VERSION=$newVersion"

# Update frontend package.json
$pattern = "`"version`":\s*`"[^`"]*`""
$replacement = "`"version`": `"$newVersion`""
Update-VersionInFile -FilePath $FrontendPackageJson -NewVersion $newVersion -Pattern $pattern -Replacement $replacement

Write-Host ""
Write-Host "Version update completed!" -ForegroundColor Green
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "   Previous: $currentVersion" -ForegroundColor White
Write-Host "   Current:  $newVersion" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "   1. Test your application" -ForegroundColor White
Write-Host "   2. Commit changes: git add . ; git commit -m `"Bump version to $newVersion`"" -ForegroundColor White
Write-Host "   3. Deploy to production" -ForegroundColor White
