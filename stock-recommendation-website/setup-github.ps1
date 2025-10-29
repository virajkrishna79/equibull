# PowerShell script to set up GitHub repository for StockAI
# Run this script in the stock-recommendation-website directory

Write-Host "🚀 Setting up GitHub repository for StockAI..." -ForegroundColor Green

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "frontend") -or -not (Test-Path "backend")) {
    Write-Host "❌ Please run this script from the stock-recommendation-website directory." -ForegroundColor Red
    exit 1
}

# Get GitHub username
$githubUsername = Read-Host "Enter your GitHub username"
if (-not $githubUsername) {
    Write-Host "❌ GitHub username is required." -ForegroundColor Red
    exit 1
}

# Check git status
Write-Host "📊 Checking git status..." -ForegroundColor Yellow
git status

# Add remote origin
Write-Host "🔗 Adding GitHub remote..." -ForegroundColor Yellow
git remote add origin "https://github.com/$githubUsername/stock-recommendation-website.git"

# Verify remote was added
Write-Host "✅ Remote added. Verifying..." -ForegroundColor Yellow
git remote -v

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Go to: https://github.com/$githubUsername/stock-recommendation-website" -ForegroundColor White
    Write-Host "2. Verify all files are uploaded correctly" -ForegroundColor White
    Write-Host "3. Make sure the repository is PUBLIC" -ForegroundColor White
    Write-Host "4. Follow the DEPLOYMENT.md guide for Vercel deployment" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Your repository URL: https://github.com/$githubUsername/stock-recommendation-website" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to push to GitHub. Please check the error above." -ForegroundColor Red
    Write-Host "💡 Make sure you have created the repository on GitHub first." -ForegroundColor Yellow
}
