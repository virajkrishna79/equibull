# 🚀 Deployment Guide for StockAI

This guide will walk you through deploying your StockAI stock recommendation website to GitHub and Vercel.

## 📋 Prerequisites

- [Git](https://git-scm.com/) installed on your machine
- [GitHub](https://github.com/) account
- [Vercel](https://vercel.com/) account
- [Node.js](https://nodejs.org/) (v16 or higher)
- [Python](https://www.python.org/) (v3.8 or higher)

## 🐙 Step 1: GitHub Repository Setup

### 1.1 Create a New GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in
2. Click the "+" icon in the top right corner and select "New repository"
3. Name your repository: `stock-recommendation-website`
4. Make it **Public** (required for free Vercel deployment)
5. Don't initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 1.2 Connect Local Repository to GitHub

```bash
# Add the remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/stock-recommendation-website.git

# Verify the remote was added
git remote -v

# Push your code to GitHub
git push -u origin master
```

### 1.3 Verify GitHub Setup

1. Go to your GitHub repository
2. Verify all files are uploaded correctly
3. Check that the repository is public

## 🌐 Step 2: Vercel Deployment

### 2.1 Connect Vercel to GitHub

1. Go to [Vercel](https://vercel.com/) and sign in
2. Click "New Project"
3. Import your GitHub repository: `stock-recommendation-website`
4. Vercel will automatically detect it's a React project

### 2.2 Configure Vercel Build Settings

**Framework Preset:** Next.js (or React if available)
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `build`
**Install Command:** `npm install`

### 2.3 Environment Variables

Add these environment variables in Vercel:

```
REACT_APP_API_URL=https://your-backend-url.com
```

**Note:** You'll need to deploy your backend separately and update this URL.

### 2.4 Deploy

1. Click "Deploy"
2. Wait for the build to complete
3. Your site will be available at `https://your-project.vercel.app`

## 🔧 Step 3: Backend Deployment

### Option A: Deploy to Railway (Recommended for Free)

1. Go to [Railway](https://railway.app/)
2. Connect your GitHub repository
3. Set environment variables from `backend/env.example`
4. Deploy the backend

### Option B: Deploy to Heroku

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create a new Heroku app
3. Set environment variables
4. Deploy using Git

### Option C: Deploy to DigitalOcean App Platform

1. Go to [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform)
2. Connect your GitHub repository
3. Configure as a Python app
4. Set environment variables

## ⚙️ Step 4: Update Configuration

### 4.1 Update Vercel Configuration

After deploying your backend, update `vercel.json`:

```json
{
  "env": {
    "REACT_APP_API_URL": "https://your-actual-backend-url.com"
  }
}
```

### 4.2 Update Frontend API Configuration

The frontend will automatically use the environment variable `REACT_APP_API_URL`.

## 🔍 Step 5: Verify Deployment

### 5.1 Test Frontend

1. Visit your Vercel URL
2. Test all features:
   - Homepage loads
   - Stock analysis works
   - Email subscription works
   - Navigation works

### 5.2 Test Backend

1. Test API endpoints:
   - `/api/health`
   - `/api/news`
   - `/api/stock/{symbol}`

### 5.3 Test Integration

1. Test frontend-backend communication
2. Verify API calls work
3. Check error handling

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails on Vercel**
   - Check build logs for errors
   - Verify all dependencies are in `package.json`
   - Ensure Node.js version compatibility

2. **API Calls Fail**
   - Verify `REACT_APP_API_URL` is set correctly
   - Check CORS configuration on backend
   - Ensure backend is running and accessible

3. **Environment Variables Not Working**
   - Restart Vercel deployment after adding variables
   - Verify variable names match exactly
   - Check for typos

### Debug Commands

```bash
# Check local build
cd frontend
npm run build

# Check git status
git status

# Check remote configuration
git remote -v

# View build logs on Vercel
# Go to your project dashboard → Deployments → View logs
```

## 📱 Post-Deployment

### 1. Custom Domain (Optional)

1. Go to Vercel project settings
2. Add your custom domain
3. Configure DNS records

### 2. Monitoring

1. Set up Vercel Analytics
2. Monitor API performance
3. Set up error tracking

### 3. Updates

1. Make changes locally
2. Commit and push to GitHub
3. Vercel will automatically redeploy

## 🎯 Next Steps

1. **Set up CI/CD** for automatic deployments
2. **Add testing** to your workflow
3. **Implement monitoring** and logging
4. **Add security headers** and HTTPS
5. **Set up backup** and disaster recovery

## 📞 Support

If you encounter issues:

1. Check Vercel documentation
2. Review GitHub repository issues
3. Check build logs for specific errors
4. Verify environment variables are set correctly

---

**Happy Deploying! 🚀**

Your StockAI website will be live and accessible to users worldwide!
