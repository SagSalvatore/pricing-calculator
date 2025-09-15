# Deployment Guide for Sagar Singh Pricing Calculator

## Deploy to Render (Recommended - Free)

### Prerequisites
1. Create a GitHub account if you don't have one
2. Create a Render account at https://render.com

### Steps:

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Pricing Calculator"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/pricing-calculator.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com and sign in
   - Click "New" > "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `sagarsingh-pricing-calculator`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app_flask:app`
   - Click "Deploy Web Service"

3. **Your app will be available at:**
   `https://sagarsingh-pricing-calculator.onrender.com/sagarsinghpricingcalculator/`

## Alternative: Deploy to Railway

1. Go to https://railway.app
2. Connect your GitHub repository
3. Railway will automatically detect it's a Python app
4. Your app will be deployed with a custom URL

## Alternative: Deploy to Koyeb

1. Go to https://koyeb.com
2. Create a new service from GitHub
3. Select your repository
4. Koyeb will handle the deployment automatically

## Environment Variables (if needed)
- No special environment variables required for this app
- The app will run on the port provided by the hosting platform

## Custom Domain (Optional)
Once deployed, you can configure a custom domain in your hosting platform's settings.

## Troubleshooting
- Make sure all files (app_flask.py, requirements.txt, Procfile, templates/) are in your GitHub repository
- Check the build logs in your hosting platform if deployment fails
- Ensure gunicorn is listed in requirements.txt