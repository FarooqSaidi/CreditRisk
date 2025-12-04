# Quick Deployment Setup

## Commands to Run

### 1. Initialize Git and Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Credit Risk Assessment System with Trust Game"

# Set main branch
git branch -M main

# Add remote (replace with your repo URL)
git remote add origin https://github.com/FarooqSaidiI/credit-risk-malawi.git

# Push to GitHub
git push -u origin main
```

### 2. Create .env files locally (for testing)

**Backend (.env in backend/ folder):**
```bash
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Frontend (.env in frontend/ folder):**
```bash
VITE_API_URL=http://localhost:8000/api
```

### 3. Test Locally Before Deploying

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

### 4. Deploy to Render

Follow the detailed steps in DEPLOYMENT.md

**Quick checklist:**
1. ✅ Code pushed to GitHub
2. ✅ Create PostgreSQL database on Render
3. ✅ Deploy backend web service
4. ✅ Deploy frontend static site
5. ✅ Update CORS settings
6. ✅ Test deployment

### 5. Environment Variables for Render

**Backend Environment Variables:**
```
SECRET_KEY=[Generate at https://djecrety.ir/]
DEBUG=False
ALLOWED_HOSTS=your-backend.onrender.com
DATABASE_URL=[From Render PostgreSQL]
CORS_ALLOWED_ORIGINS=https://your-frontend.onrender.com
```

**Frontend Environment Variables:**
```
VITE_API_URL=https://your-backend.onrender.com/api
```

### 6. Post-Deployment

```bash
# Create superuser (in Render Shell)
python manage.py createsuperuser

# Access admin panel
https://your-backend.onrender.com/admin
```

## Repository Name Suggestions

- `credit-risk-malawi`
- `microfinance-risk-assessment`
- `trust-game-lending`
- `malawi-credit-scoring`

## Important Notes

1. **Free Tier Limitations**: Backend sleeps after 15 min inactivity
2. **First Request**: May take 30-60 seconds to wake up
3. **Database**: Free for 90 days, then $7/month
4. **Custom Domain**: Optional, can add later

## Need Help?

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Check DEPLOYMENT.md for detailed troubleshooting
