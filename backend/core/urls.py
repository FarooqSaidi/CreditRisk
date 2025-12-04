"""
URL configuration for core app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BranchViewSet, LoanOfficerViewSet, BorrowerViewSet,
    SpouseViewSet, GuarantorViewSet, LoanViewSet,
    CollateralViewSet, RepaymentViewSet, RecoveryViewSet,
    LoanRiskMetricViewSet, GroupRiskMetricViewSet, MacroMonthlyViewSet,
    ClientScreeningViewSet, ClientProfileViewSet, InformalLoanViewSet,
    SpouseAssessmentViewSet, GuarantorAssessmentViewSet, HouseholdAssessmentViewSet,
    BusinessAssessmentViewSet, BusinessItemViewSet, ClientCollateralViewSet,
    GuarantorCollateralViewSet, BehavioralVerificationViewSet
)

# Temporarily disabled Bayesian models (requires numpy, scipy, pymc)
# from .model_views import RiskModelView

# Create router and register viewsets
router = DefaultRouter()
# router.register(r'models', RiskModelView, basename='models')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'loan-officers', LoanOfficerViewSet, basename='loan-officer')
router.register(r'borrowers', BorrowerViewSet, basename='borrower')
router.register(r'spouses', SpouseViewSet, basename='spouse')
router.register(r'guarantors', GuarantorViewSet, basename='guarantor')
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'collateral', CollateralViewSet, basename='collateral')
router.register(r'repayments', RepaymentViewSet, basename='repayment')
router.register(r'recoveries', RecoveryViewSet, basename='recovery')
router.register(r'risk-metrics/loan', LoanRiskMetricViewSet, basename='loan-risk-metric')
router.register(r'risk-metrics/group', GroupRiskMetricViewSet, basename='group-risk-metric')
router.register(r'macro-monthly', MacroMonthlyViewSet, basename='macro-monthly')

# Client Screening Routes
router.register(r'client-screenings', ClientScreeningViewSet, basename='client-screening')
router.register(r'client-profiles', ClientProfileViewSet, basename='client-profile')
router.register(r'informal-loans', InformalLoanViewSet, basename='informal-loan')
router.register(r'spouse-assessments', SpouseAssessmentViewSet, basename='spouse-assessment')
router.register(r'guarantor-assessments', GuarantorAssessmentViewSet, basename='guarantor-assessment')
router.register(r'household-assessments', HouseholdAssessmentViewSet, basename='household-assessment')
router.register(r'business-assessments', BusinessAssessmentViewSet, basename='business-assessment')
router.register(r'business-items', BusinessItemViewSet, basename='business-item')
router.register(r'client-collaterals', ClientCollateralViewSet, basename='client-collateral')
router.register(r'guarantor-collaterals', GuarantorCollateralViewSet, basename='guarantor-collateral')
router.register(r'behavioral-verifications', BehavioralVerificationViewSet, basename='behavioral-verification')


urlpatterns = [
    path('', include(router.urls)),
]
