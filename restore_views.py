"""
Script to restore views.py to a working state
"""

# Read the backup file
try:
    with open('backend/core/views.py.backup', 'r', encoding='utf-8') as f:
        content = f.read()
except:
    print("No backup found, creating minimal views.py")
    content = None

if content and len(content) > 10000:  # If backup seems valid
    # Use the backup
    with open('backend/core/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Restored from backup")
else:
    # Create minimal working views.py
    minimal_views = '''"""
Django REST Framework ViewSets for all models
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Branch, LoanOfficer, Borrower, Spouse, Guarantor,
    Loan, Collateral, Repayment, Recovery,
    LoanRiskMetric, GroupRiskMetric, MacroMonthly
)
from .serializers import (
    BranchSerializer, LoanOfficerSerializer, BorrowerSerializer, BorrowerListSerializer,
    SpouseSerializer, GuarantorSerializer, LoanSerializer, LoanListSerializer,
    CollateralSerializer, RepaymentSerializer, RecoverySerializer,
    LoanRiskMetricSerializer, GroupRiskMetricSerializer, MacroMonthlySerializer,
    LoanStatisticsSerializer, RepaymentStatisticsSerializer, PortfolioMetricsSerializer
)


class BranchViewSet(viewsets.ModelViewSet):
    """ViewSet for Branch model"""
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filterset_fields = ['name']
    search_fields = ['name', 'code']


class LoanOfficerViewSet(viewsets.ModelViewSet):
    """ViewSet for LoanOfficer model"""
    queryset = LoanOfficer.objects.all()
    serializer_class = LoanOfficerSerializer
    filterset_fields = ['branch', 'is_active']
    search_fields = ['first_name', 'last_name', 'employee_id']


class BorrowerViewSet(viewsets.ModelViewSet):
    """ViewSet for Borrower model"""
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    filterset_fields = ['district', 'business_industry', 'gender']
    search_fields = ['first_name', 'last_name', 'national_id']


class SpouseViewSet(viewsets.ModelViewSet):
    """ViewSet for Spouse model"""
    queryset = Spouse.objects.all()
    serializer_class = SpouseSerializer
    filterset_fields = ['employment_status']


class GuarantorViewSet(viewsets.ModelViewSet):
    """ViewSet for Guarantor model"""
    queryset = Guarantor.objects.all()
    serializer_class = GuarantorSerializer
    filterset_fields = ['borrower', 'relationship_to_borrower', 'employment_status']
    search_fields = ['first_name', 'last_name', 'national_id']


class LoanViewSet(viewsets.ModelViewSet):
    """ViewSet for Loan model"""
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    filterset_fields = ['branch', 'loan_type', 'status']
    search_fields = ['loan_number', 'borrower__first_name', 'borrower__last_name']


class CollateralViewSet(viewsets.ModelViewSet):
    """ViewSet for Collateral model"""
    queryset = Collateral.objects.all()
    serializer_class = CollateralSerializer
    filterset_fields = ['loan', 'collateral_type', 'condition', 'owner_type']


class RepaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Repayment model"""
    queryset = Repayment.objects.all()
    serializer_class = RepaymentSerializer
    filterset_fields = ['loan', 'payment_status']
    ordering_fields = ['scheduled_date', 'actual_payment_date']


class RecoveryViewSet(viewsets.ModelViewSet):
    """ViewSet for Recovery model"""
    queryset = Recovery.objects.all()
    serializer_class = RecoverySerializer
    filterset_fields = ['loan']
    ordering_fields = ['recovery_date', 'recovery_amount']


class LoanRiskMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for LoanRiskMetric model"""
    queryset = LoanRiskMetric.objects.all()
    serializer_class = LoanRiskMetricSerializer
    filterset_fields = ['loan']


class GroupRiskMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for GroupRiskMetric model"""
    queryset = GroupRiskMetric.objects.all()
    serializer_class = GroupRiskMetricSerializer
    filterset_fields = ['branch', 'loan_type', 'tenure_months']


class MacroMonthlyViewSet(viewsets.ModelViewSet):
    """ViewSet for MacroMonthly model"""
    queryset = MacroMonthly.objects.all()
    serializer_class = MacroMonthlySerializer
    ordering_fields = ['month_date']
    ordering = ['-month_date']
'''
    
    with open('backend/core/views.py', 'w', encoding='utf-8') as f:
        f.write(minimal_views)
    print("Created minimal working views.py")
