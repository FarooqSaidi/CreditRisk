# Credit Risk Assessment System

AI-powered microfinance credit risk assessment platform for Malawi, featuring comprehensive client screening, trust game assessments, and Bayesian risk modeling.

## Features

- **Comprehensive Client Screening**: Multi-step form for detailed borrower assessment
- **Trust Game Assessments**: Behavioral economics-based evaluation for spouses and guarantors
- **Risk-Based Loan Recommendations**: Automatic loan amount adjustments based on trust scores
- **Bayesian Risk Modeling**: Advanced probability of default (PD) and loss given default (LGD) calculations
- **Portfolio Analytics**: Real-time risk metrics and portfolio monitoring
- **Malawi-Specific Context**: Tailored for local microfinance practices including informal loans (Katapila)

## Tech Stack

### Backend
- Django 5.2.8
- Django REST Framework
- SQLite (development) / PostgreSQL (production)
- Python 3.11+

### Frontend
- React 18
- Vite
- TailwindCSS
- Framer Motion
- Recharts
- Lucide Icons

## Local Development Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Run development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Deployment to Render

### Backend Deployment

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/FarooqSaidiI/your-repo-name.git
git push -u origin main
```

2. Create a new Web Service on Render:
   - Connect your GitHub repository
   - Root Directory: `backend`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn creditrisk.wsgi:application`
   - Add environment variables:
     - `SECRET_KEY`: Generate a secure key
     - `DEBUG`: `False`
     - `ALLOWED_HOSTS`: `your-app.onrender.com`
     - `DATABASE_URL`: (Render will provide PostgreSQL URL)
     - `CORS_ALLOWED_ORIGINS`: `https://your-frontend.onrender.com`

3. Add PostgreSQL database:
   - Create a new PostgreSQL database on Render
   - Copy the Internal Database URL
   - Add it as `DATABASE_URL` environment variable

### Frontend Deployment

1. Create a new Static Site on Render:
   - Connect your GitHub repository
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Add environment variable:
     - `VITE_API_URL`: `https://your-backend.onrender.com/api`

2. Update backend CORS settings:
   - Add your frontend URL to `CORS_ALLOWED_ORIGINS`
   - Add to `ALLOWED_HOSTS`

## Trust Game Assessment

The system includes detailed trust assessments for both spouses and guarantors:

### Spouse Assessment (4 Questions)
1. **Financial Transparency Test** - Evaluates money disclosure habits
2. **Repayment Crisis Response** - Tests willingness to help during shortfalls
3. **Joint Responsibility Awareness** - Measures shared accountability
4. **Loan Purpose Alignment** - Assesses support for loan usage

### Guarantor Assessment (4 Questions)
1. **Relationship Depth Test** - Verifies relationship duration and quality
2. **Financial Commitment Test** - Tests actual willingness to pay
3. **Asset Pledge Willingness** - Measures collateral commitment
4. **Tracking & Enforcement Ability** - Evaluates ability to locate client

### Risk-Based Decisions
- **Score < 40**: REJECT (0% of requested amount)
- **Score 40-59**: CONDITIONAL (60% of requested amount)
- **Score 60-79**: ACCEPT (80% of requested amount)
- **Score 80+**: ACCEPT (100% of requested amount)

## API Endpoints

### Core Endpoints
- `/api/borrowers/` - Borrower management
- `/api/loans/` - Loan operations
- `/api/client-screenings/` - Comprehensive screening
- `/api/spouse-assessments/` - Spouse trust game
- `/api/guarantor-assessments/` - Guarantor trust game
- `/api/risk-metrics/` - Risk calculations

### Statistics
- `/api/loans/statistics/` - Loan aggregates
- `/api/loans/portfolio_metrics/` - Portfolio risk metrics
- `/api/repayments/statistics/` - Repayment performance

## Project Structure

```
.
├── backend/
│   ├── core/                 # Main Django app
│   │   ├── models.py        # Database models
│   │   ├── views.py         # API views
│   │   ├── serializers.py   # DRF serializers
│   │   └── urls.py          # URL routing
│   ├── creditrisk/          # Django project settings
│   ├── requirements.txt     # Python dependencies
│   └── build.sh            # Render build script
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

GitHub: [@FarooqSaidiI](https://github.com/FarooqSaidiI)

## Acknowledgments

- Built for microfinance institutions in Malawi
- Incorporates behavioral economics principles
- Uses Bayesian statistical modeling for risk assessment
