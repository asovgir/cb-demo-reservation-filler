# Quick Deployment Guide

## Fastest Way to Deploy (Render - Free)

1. Go to https://render.com and sign up/login

2. Click **"New +"** → **"Web Service"**

3. Connect this GitHub repository (you'll need to push it to GitHub first)

4. Configure:
   - **Name**: `cloudbeds-creator` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: Leave empty (will use Procfile)
   - **Instance Type**: `Free`

5. Add Environment Variables:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = Generate a random string (e.g., use https://randomkeygen.com/)

6. Click **"Create Web Service"**

7. Wait 2-3 minutes for deployment

8. Access your app at the provided URL!

## If You Don't Have GitHub Yet

### Option A: Use GitHub (Recommended)

1. Create a GitHub account at https://github.com
2. Create a new repository
3. Push this code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
   git push -u origin main
   ```
4. Follow Render steps above

### Option B: Use Render's Direct Upload

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Choose **"Deploy an existing image from a registry"** or **"Public Git repository"**
4. You can also zip this folder and upload directly in some cases

### Option C: Use Railway (Also Free)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects everything!
6. Add environment variable `SECRET_KEY` in settings
7. Done!

## Need Help?

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Heroku Docs**: https://devcenter.heroku.com

## Testing Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py

# Open browser to http://localhost:5000
```

## Important Notes

- **Secret Key**: Always set a unique SECRET_KEY in production
- **HTTPS**: Both Render and Railway provide free HTTPS
- **Logs**: Check your platform's logs to monitor reservation creation
- **Free Tier**: Free tiers may sleep after inactivity but wake up quickly
