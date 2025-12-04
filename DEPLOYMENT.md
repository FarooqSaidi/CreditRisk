# Deployment Guide

## Step-by-Step Deployment to Render

### Prerequisites
- GitHub account
- Render account (free tier available)
- Git installed locally

### Step 1: Push to GitHub

1. Initialize git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit: Credit Risk Assessment System"
```

2. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Repository name: `credit-risk-malawi` (or your preferred name)
   - Make it public or private
   - Don't initialize with README (we already have one)

3. Push to GitHub:
```bash
git branch -M main
git remote add origin https://github.com/FarooqSaidiI/credit-risk-malawi.git
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. **Create PostgreSQL Database**
   - Go to https://dashboard.render.com
   - Click "New +" → "PostgreSQL"
   - Name: `creditrisk-db`
   - Database: `creditrisk`
   - User: `creditrisk_user`
   - Region: Choose closest to your users
   - Plan: Free (or paid for production)
   - Click "Create Database"
   - **Copy the Internal Database URL** (you'll need this)

2. **Create Web Service for Backend**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `creditrisk-backend`
     - **Root Directory**: `backend`
     - **Environment**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn creditrisk.wsgi:application`
     - **Plan**: Free (or paid for production)

3. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable":
   
   ```
   SECRET_KEY = [Generate a secure key - use https://djecrety.ir/]
   DEBUG = False
   ALLOWED_HOSTS = creditrisk-backend.onrender.com
   DATABASE_URL = [Paste the Internal Database URL from step 1]
   CORS_ALLOWED_ORIGINS = https://creditrisk-frontend.onrender.com
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Once deployed, note your backend URL: `https://creditrisk-backend.onrender.com`

5. **Run Initial Setup** (Optional - if you need sample data)
   - Go to your service → "Shell" tab
   - Run:
   ```bash
   python manage.py createsuperuser
   ```

### Step 3: Deploy Frontend to Render

1. **Create Static Site**
   - Click "New +" → "Static Site"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `creditrisk-frontend`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm install && npm run build`
     - **Publish Directory**: `dist`

2. **Add Environment Variable**
   ```
   VITE_API_URL = https://creditrisk-backend.onrender.com/api
   ```

3. **Deploy**
   - Click "Create Static Site"
   - Wait for deployment (3-5 minutes)
   - Your app will be live at: `https://creditrisk-frontend.onrender.com`

### Step 4: Update Backend CORS Settings

1. Go back to your backend service on Render
2. Update environment variables:
   ```
   CORS_ALLOWED_ORIGINS = https://creditrisk-frontend.onrender.com
   ALLOWED_HOSTS = creditrisk-backend.onrender.com,creditrisk-frontend.onrender.com
   ```
3. Save changes (this will trigger a redeploy)

### Step 5: Test Your Deployment

1. Visit your frontend URL: `https://creditrisk-frontend.onrender.com`
2. Test the following:
   - Dashboard loads correctly
   - Can view borrowers
   - Can create a new screening
   - Trust game assessments work
   - Risk calculations complete

### Troubleshooting

#### Backend Issues

**500 Internal Server Error**
- Check logs in Render dashboard
- Verify DATABASE_URL is correct
- Ensure migrations ran successfully
- Check SECRET_KEY is set

**CORS Errors**
- Verify CORS_ALLOWED_ORIGINS includes your frontend URL
- Check ALLOWED_HOSTS includes both backend and frontend URLs
- Ensure no trailing slashes in URLs

**Database Connection Failed**
- Verify DATABASE_URL is the Internal Database URL
- Check database is running
- Ensure database user has correct permissions

#### Frontend Issues

**API Calls Failing**
- Check VITE_API_URL is correct
- Verify backend is running
- Check browser console for CORS errors

**Build Fails**
- Check all dependencies are in package.json
- Verify Node version compatibility
- Check for syntax errors in code

**Blank Page**
- Check browser console for errors
- Verify build completed successfully
- Check API URL is accessible

### Free Tier Limitations

**Render Free Tier:**
- Backend: Spins down after 15 minutes of inactivity (first request may be slow)
- Database: 90 days free, then $7/month
- Static Site: Always on, no limitations

**Recommendations for Production:**
- Upgrade to paid plans for better performance
- Use a custom domain
- Enable automatic deployments on git push
- Set up monitoring and alerts

### Custom Domain Setup (Optional)

1. **Backend**
   - Go to your backend service → Settings
   - Add custom domain: `api.yourdomain.com`
   - Update DNS records as instructed

2. **Frontend**
   - Go to your static site → Settings
   - Add custom domain: `yourdomain.com`
   - Update DNS records as instructed

3. **Update Environment Variables**
   - Update CORS_ALLOWED_ORIGINS
   - Update VITE_API_URL
   - Update ALLOWED_HOSTS

### Continuous Deployment

Render automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Both frontend and backend will redeploy automatically.

### Monitoring

1. **Render Dashboard**
   - View logs in real-time
   - Monitor resource usage
   - Check deployment history

2. **Django Admin**
   - Access at: `https://creditrisk-backend.onrender.com/admin`
   - Login with superuser credentials
   - Monitor database records

### Backup Strategy

1. **Database Backups**
   - Render PostgreSQL includes automatic backups
   - Download manual backups from dashboard
   - Consider external backup service for production

2. **Code Backups**
   - GitHub serves as code backup
   - Tag releases for version control
   - Keep local copies

### Security Checklist

- ✅ DEBUG = False in production
- ✅ SECRET_KEY is unique and secure
- ✅ ALLOWED_HOSTS is properly configured
- ✅ CORS_ALLOWED_ORIGINS is restrictive
- ✅ Database credentials are secure
- ✅ HTTPS is enabled (automatic on Render)
- ✅ Environment variables are not in code
- ✅ .gitignore excludes sensitive files

### Support

If you encounter issues:
1. Check Render documentation: https://render.com/docs
2. Review Django deployment guide: https://docs.djangoproject.com/en/5.2/howto/deployment/
3. Check application logs in Render dashboard
4. Review this deployment guide

### Next Steps

After successful deployment:
1. Populate database with sample data
2. Test all features thoroughly
3. Set up monitoring and alerts
4. Configure backup strategy
5. Add custom domain (optional)
6. Share with users!

---

**Your URLs:**
- Frontend: `https://creditrisk-frontend.onrender.com`
- Backend: `https://creditrisk-backend.onrender.com`
- Admin: `https://creditrisk-backend.onrender.com/admin`
- API Docs: `https://creditrisk-backend.onrender.com/api`
