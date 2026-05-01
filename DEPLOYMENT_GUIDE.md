# 🚀 DEPLOYMENT GUIDE - Render.com

**Date**: May 2, 2026  
**Application**: AI Resume Analyzer - Career Readiness Platform  
**Version**: 2.0.0

---

## 📋 PREREQUISITES

Before deploying, make sure you have:
- ✅ GitHub account
- ✅ Code pushed to GitHub: https://github.com/Sapan02206/Resume_Analyzer
- ✅ Render.com account (free - sign up with GitHub)

---

## 🎯 STEP-BY-STEP DEPLOYMENT

### **Step 1: Sign Up for Render**

1. Go to: https://render.com
2. Click **"Get Started"**
3. Click **"Sign in with GitHub"**
4. Authorize Render to access your GitHub account

---

### **Step 2: Create New Web Service**

1. On Render Dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Find and select: **`Sapan02206/Resume_Analyzer`**
5. Click **"Connect"**

---

### **Step 3: Configure Web Service**

Fill in the following settings:

#### **Basic Settings:**
- **Name**: `resume-analyzer` (or any name you prefer)
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt, Singapore)
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

#### **Build & Deploy:**
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```

- **Start Command**: 
  ```
  gunicorn app:app
  ```

#### **Instance Type:**
- Select **"Free"** (for testing)
- Or **"Starter"** ($7/month for better performance)

---

### **Step 4: Add Environment Variables**

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Click "Generate" | Auto-generated secure key |
| `PYTHON_VERSION` | `3.11.0` | Python version |
| `DATABASE_URL` | (Leave for now) | Will add after creating database |

---

### **Step 5: Create PostgreSQL Database**

1. Go back to Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `resume-analyzer-db`
   - **Database**: `resume_analyzer`
   - **User**: `resume_user`
   - **Region**: Same as your web service
   - **Instance Type**: **Free**
4. Click **"Create Database"**
5. Wait 2-3 minutes for database to be ready

---

### **Step 6: Connect Database to Web Service**

1. Go to your database: `resume-analyzer-db`
2. Copy the **"Internal Database URL"** (starts with `postgresql://`)
3. Go back to your web service: `resume-analyzer`
4. Click **"Environment"** tab
5. Add new environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL
6. Click **"Save Changes"**

---

### **Step 7: Deploy!**

1. Click **"Create Web Service"** button at the bottom
2. Render will start building your application
3. Watch the logs - you'll see:
   ```
   ==> Downloading dependencies
   ==> Installing packages
   ==> Building application
   ==> Starting server
   ```
4. Wait 5-10 minutes for first deployment
5. Once you see **"Your service is live 🎉"**, it's ready!

---

### **Step 8: Initialize Database**

After first deployment, you need to create database tables:

1. In Render Dashboard, go to your web service
2. Click **"Shell"** tab
3. Run these commands:
   ```bash
   python
   ```
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
   exit()
   ```

Or create a one-time job to initialize:
1. Click **"New +"** → **"Background Worker"**
2. Use same repo
3. **Start Command**: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`
4. Run once and delete

---

### **Step 9: Access Your Application**

Your app will be available at:
```
https://resume-analyzer.onrender.com
```
(Replace `resume-analyzer` with your chosen name)

**Test it:**
- Homepage: `https://resume-analyzer.onrender.com/`
- Demo Mode: `https://resume-analyzer.onrender.com/demo`
- Dashboard: `https://resume-analyzer.onrender.com/career-dashboard`

---

## 🌐 CONNECT CUSTOM DOMAIN (Optional)

### **Option A: Subdomain (Recommended)**

1. In Render, go to your web service
2. Click **"Settings"** → **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Enter: `resume-analyzer.sapandesai.me`
5. Render will show DNS records to add
6. Go to your domain provider (where you bought sapandesai.me)
7. Add CNAME record:
   ```
   Type: CNAME
   Name: resume-analyzer
   Value: resume-analyzer.onrender.com
   TTL: 3600
   ```
8. Wait 5-60 minutes for DNS propagation
9. Access at: `https://resume-analyzer.sapandesai.me`

### **Option B: Root Domain**

1. In Render, add custom domain: `sapandesai.me`
2. Add A records to your domain:
   ```
   Type: A
   Name: @
   Value: [IP from Render]
   TTL: 3600
   ```
3. Access at: `https://sapandesai.me`

---

## 🔧 TROUBLESHOOTING

### **Issue: Build Failed**

**Check:**
- All dependencies in `requirements.txt`
- Python version matches `runtime.txt`
- No syntax errors in code

**Solution:**
- Check build logs in Render
- Fix errors and push to GitHub
- Render auto-deploys on push

---

### **Issue: Application Crashes**

**Check:**
- Environment variables set correctly
- Database connected
- Logs in Render dashboard

**Solution:**
- Click "Logs" tab to see error
- Add missing environment variables
- Restart service

---

### **Issue: Database Connection Error**

**Check:**
- `DATABASE_URL` environment variable set
- Database is running (green status)
- Using Internal Database URL (not External)

**Solution:**
- Copy Internal Database URL from database page
- Update `DATABASE_URL` in web service
- Restart service

---

### **Issue: 404 Not Found**

**Check:**
- Accessing correct URL
- Service is deployed (green status)
- Routes exist in `app.py`

**Solution:**
- Check service status
- View logs for errors
- Test with `/demo` route first

---

## 📊 MONITORING

### **View Logs**
1. Go to your web service in Render
2. Click **"Logs"** tab
3. See real-time application logs

### **Check Metrics**
1. Click **"Metrics"** tab
2. See:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### **Set Up Alerts**
1. Click **"Settings"** → **"Notifications"**
2. Add email for deployment notifications
3. Get notified of:
   - Successful deployments
   - Failed deployments
   - Service crashes

---

## 🔄 CONTINUOUS DEPLOYMENT

Render automatically deploys when you push to GitHub:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. Render detects the push
4. Automatically builds and deploys
5. New version live in 5-10 minutes!

---

## 💰 PRICING

### **Free Tier**
- ✅ Web Service: Free (spins down after 15 min inactivity)
- ✅ PostgreSQL: Free (90 days, then $7/month)
- ✅ 750 hours/month
- ⚠️ Slow cold starts (30-60 seconds)

### **Paid Tier (Recommended for Production)**
- 💵 Web Service: $7/month (Starter)
- 💵 PostgreSQL: $7/month
- ✅ Always on (no cold starts)
- ✅ Better performance
- ✅ More resources

---

## ✅ POST-DEPLOYMENT CHECKLIST

After deployment, verify:

- [ ] Homepage loads: `https://your-app.onrender.com/`
- [ ] Demo mode works: `https://your-app.onrender.com/demo`
- [ ] Can upload resume
- [ ] Dashboard displays
- [ ] Can add projects
- [ ] Progress tracking works
- [ ] All features functional
- [ ] No errors in logs
- [ ] Database connected
- [ ] Environment variables set

---

## 🎉 SUCCESS!

Your AI Resume Analyzer is now live on the internet!

**Share your app:**
- Direct link: `https://resume-analyzer.onrender.com`
- Custom domain: `https://resume-analyzer.sapandesai.me`
- Add to portfolio
- Share on LinkedIn
- Show to recruiters

---

## 📞 SUPPORT

### **Render Documentation**
- https://render.com/docs

### **Common Issues**
- Check Render Community: https://community.render.com
- Check logs in Render dashboard
- Review this guide

### **Need Help?**
- Render Support: support@render.com
- Check `COMPLETE_DOCUMENTATION.md` for app details

---

**Deployment Guide Complete!** 🚀

*Follow these steps and your app will be live in 15-20 minutes!*
