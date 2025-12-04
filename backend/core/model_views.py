"""
API Views for Bayesian Risk Models
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
import numpy as np
import pandas as pd
from django.db.models import F
import pickle
import os
from django.conf import settings

from .models import Loan, LoanRiskMetric
from .serializers import LoanRiskMetricSerializer
from .bayesian_models import BayesianPDModel, BayesianLGDModel, BayesianHazardModel

# Global model instances (in a real app, these would be loaded from storage)
pd_model = BayesianPDModel()
lgd_model = BayesianLGDModel()
hazard_model = BayesianHazardModel()

MODEL_DIR = os.path.join(settings.BASE_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

class RiskModelView(viewsets.ViewSet):
    """
    ViewSet for interacting with Bayesian Risk Models
    """
    
    @action(detail=False, methods=['post'])
    def train(self, request):
        """
        Train models on current historical data
        """
        # 1. Prepare Data for PD Model
        # Target: Defaulted (1) vs Paid Off/Active (0)
        # Features: Loan Amount, Interest Rate, Tenure, Borrower Income
        
        loans = Loan.objects.exclude(status='PENDING').select_related('borrower')
        
        if not loans.exists():
            return Response({"error": "No data to train on"}, status=status.HTTP_400_BAD_REQUEST)
            
        data = []
        targets = []
        
        for loan in loans:
            # Define Default: Status is DEFAULTED or WRITTEN_OFF
            is_default = 1 if loan.status in ['DEFAULTED', 'WRITTEN_OFF'] else 0
            
            # Features
            features = [
                float(loan.principal_amount),
                float(loan.monthly_interest_rate),
                float(loan.tenure_months),
                float(loan.borrower.monthly_income)
            ]
            
            data.append(features)
            targets.append(is_default)
            
        X = np.array(data)
        y = np.array(targets)
        
        # Normalize features (simple scaling)
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0) + 1e-8
        X_scaled = (X - self.mean) / self.std
        
        # Add intercept
        X_final = np.c_[np.ones(X_scaled.shape[0]), X_scaled]
        
        # Train PD Model
        pd_model.fit(X_final, y)
        
        # Train LGD Model (simplified)
        # Get recovery rates for defaulted loans
        defaulted_loans = Loan.objects.filter(status__in=['DEFAULTED', 'WRITTEN_OFF'])
        observed_lgds = []
        for loan in defaulted_loans:
            # LGD = 1 - (Recoveries / EAD)
            recoveries = sum(r.recovery_amount for r in loan.recoveries.all())
            ead = loan.principal_amount # Simplified EAD
            recovery_rate = float(recoveries / ead) if ead > 0 else 0
            lgd = max(0.0, min(1.0, 1.0 - recovery_rate))
            observed_lgds.append(lgd)
            
        lgd_model.update(np.array(observed_lgds))
        
        # Save models (simplified)
        self._save_models()
        
        return Response({
            "message": "Models trained successfully",
            "pd_coef_mean": pd_model.coef_mean.tolist() if pd_model.coef_mean is not None else [],
            "lgd_params": {"alpha": lgd_model.alpha, "beta": lgd_model.beta},
            "training_samples": len(data)
        })

    @action(detail=False, methods=['post'])
    def predict(self, request):
        """
        Predict risk metrics for a specific loan (or hypothetical)
        """
        loan_id = request.data.get('loan_id')
        
        if loan_id:
            try:
                loan = Loan.objects.get(id=loan_id)
                features = [
                    float(loan.principal_amount),
                    float(loan.monthly_interest_rate),
                    float(loan.tenure_months),
                    float(loan.borrower.monthly_income)
                ]
            except Loan.DoesNotExist:
                return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Hypothetical data
            features = request.data.get('features')
            if not features or len(features) != 4:
                return Response({"error": "Provide loan_id or features [amount, rate, tenure, income]"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Preprocess
        # Note: In production, load saved scalers
        if not hasattr(self, 'mean'):
            # Fallback if not trained
            X_scaled = np.array(features).reshape(1, -1)
            X_final = np.c_[np.ones(1), X_scaled]
        else:
            X_scaled = (np.array(features) - self.mean) / self.std
            X_final = np.c_[np.ones(1), X_scaled.reshape(1, -1)]
            
        # Predict PD
        pd_result = pd_model.predict_proba(X_final)
        
        # Predict LGD (Global model for now, could be conditional)
        lgd_result = lgd_model.predict()
        
        # Calculate Expected Loss
        # EL = PD * LGD * EAD
        ead = features[0] # Principal amount
        el = pd_result.mean * lgd_result.mean * ead
        
        return Response({
            "pd": {
                "mean": pd_result.mean,
                "lower_hdi": pd_result.lower_hdi,
                "upper_hdi": pd_result.upper_hdi
            },
            "lgd": {
                "mean": lgd_result.mean,
                "lower_hdi": lgd_result.lower_hdi,
                "upper_hdi": lgd_result.upper_hdi
            },
            "expected_loss": el,
            "ead": ead
        })

    def _save_models(self):
        # Save to pickle
        with open(os.path.join(MODEL_DIR, 'pd_model.pkl'), 'wb') as f:
            pickle.dump(pd_model, f)
        with open(os.path.join(MODEL_DIR, 'lgd_model.pkl'), 'wb') as f:
            pickle.dump(lgd_model, f)
        # Save scalers too in real app
