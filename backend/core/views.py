"""
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
    LoanRiskMetric, GroupRiskMetric, MacroMonthly,
    ClientScreening, ClientProfile, InformalLoan, SpouseAssessment,
    GuarantorAssessment, HouseholdAssessment, BusinessAssessment,
    BusinessItem, ClientCollateral, GuarantorCollateral, BehavioralVerification
)
from .serializers import (
    BranchSerializer, LoanOfficerSerializer, BorrowerSerializer, BorrowerListSerializer,
    SpouseSerializer, GuarantorSerializer, LoanSerializer, LoanListSerializer,
    CollateralSerializer, RepaymentSerializer, RecoverySerializer,
    LoanRiskMetricSerializer, GroupRiskMetricSerializer, MacroMonthlySerializer,
    LoanStatisticsSerializer, RepaymentStatisticsSerializer, PortfolioMetricsSerializer,
    ClientScreeningSerializer, ClientProfileSerializer, InformalLoanSerializer,
    SpouseAssessmentSerializer, GuarantorAssessmentSerializer, HouseholdAssessmentSerializer,
    BusinessAssessmentSerializer, BusinessItemSerializer, ClientCollateralSerializer,
    GuarantorCollateralSerializer, BehavioralVerificationSerializer
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

    @action(detail=True, methods=['get'])
    def loans(self, request, pk=None):
        """
        Get loans for a specific borrower
        """
        borrower = self.get_object()
        loans = Loan.objects.filter(borrower=borrower)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)


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

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get aggregated loan statistics
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Basic aggregates
        total_loans = queryset.count()
        total_principal = queryset.aggregate(Sum('principal_amount'))['principal_amount__sum'] or 0
        active_loans = queryset.filter(status='ACTIVE').count()
        defaulted_loans = queryset.filter(status='DEFAULTED').count()
        avg_loan_amount = queryset.aggregate(Avg('principal_amount'))['principal_amount__avg'] or 0
        
        # Group by Loan Type
        by_loan_type = {}
        type_stats = queryset.values('loan_type').annotate(count=Count('id'))
        for stat in type_stats:
            by_loan_type[stat['loan_type']] = stat['count']
            
        # Group by Branch
        by_branch = {}
        branch_stats = queryset.values('branch__name').annotate(count=Count('id'))
        for stat in branch_stats:
            by_branch[stat['branch__name']] = stat['count']
            
        data = {
            "total_loans": total_loans,
            "total_principal": total_principal,
            "active_loans": active_loans,
            "defaulted_loans": defaulted_loans,
            "avg_loan_amount": avg_loan_amount,
            "by_loan_type": by_loan_type,
            "by_branch": by_branch
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def portfolio_metrics(self, request):
        """
        Get portfolio-level risk metrics
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        total_outstanding = queryset.filter(status='ACTIVE').aggregate(Sum('principal_amount'))['principal_amount__sum'] or 0
        
        # Simplified PAR calculations (mock logic for now as we don't have full arrears history in this view)
        # In a real app, we'd query Repayments with days_late > 30
        
        # Mocking PAR based on status for demonstration
        par30_loans = queryset.filter(status='ACTIVE', repayments__days_late__gt=30).distinct()
        par30_amount = par30_loans.aggregate(Sum('principal_amount'))['principal_amount__sum'] or 0
        
        par30_rate = (par30_amount / total_outstanding) if total_outstanding > 0 else 0
        
        # Bayesian Model Aggregates (Mocked or fetched from RiskMetric)
        # In a real app, we'd aggregate the LoanRiskMetric values
        avg_pd = queryset.aggregate(Avg('risk_metric__pd_mean'))['risk_metric__pd_mean__avg'] or 0.05
        avg_lgd = queryset.aggregate(Avg('risk_metric__lgd_mean'))['risk_metric__lgd_mean__avg'] or 0.45
        
        data = {
            "par30_rate": par30_rate,
            "par60_rate": par30_rate * Decimal('0.6'), # Mock
            "par90_rate": par30_rate * Decimal('0.3'), # Mock
            "total_outstanding": total_outstanding,
            "total_at_risk_30": par30_amount,
            "pd_rate": avg_pd,
            "lgd_rate": avg_lgd,
            "portfolio_var": float(total_outstanding) * float(avg_pd) * float(avg_lgd) # Simplified VaR
        }
        return Response(data)


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

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get repayment statistics
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        total_repayments = queryset.count()
        on_time_count = queryset.filter(payment_status='ON_TIME').count()
        late_count = queryset.filter(payment_status='LATE_PAYMENT').count()
        partial_count = queryset.filter(payment_status='PARTIAL_PAYMENT').count()
        missed_count = queryset.filter(payment_status='MISSED_PAYMENT').count()
        
        on_time_rate = (on_time_count / total_repayments) if total_repayments > 0 else 0
        avg_days_late = queryset.filter(days_late__gt=0).aggregate(Avg('days_late'))['days_late__avg'] or 0
        
        data = {
            "total_repayments": total_repayments,
            "on_time_count": on_time_count,
            "late_count": late_count,
            "partial_count": partial_count,
            "missed_count": missed_count,
            "on_time_rate": on_time_rate,
            "avg_days_late": avg_days_late
        }
        return Response(data)


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
    filterset_fields = ['screening', 'spouse_verified', 'guarantor_verified', 'community_verified']


class ClientScreeningViewSet(viewsets.ModelViewSet):
    """ViewSet for comprehensive client screening"""
    queryset = ClientScreening.objects.all()
    serializer_class = ClientScreeningSerializer
    filterset_fields = ['borrower', 'status', 'cluster_group']
    ordering_fields = ['screening_date', 'client_risk_score']


class ClientProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for client profile and identity"""
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    filterset_fields = ['screening', 'education_level', 'residence_type']


class InformalLoanViewSet(viewsets.ModelViewSet):
    """ViewSet for informal loans"""
    queryset = InformalLoan.objects.all()
    serializer_class = InformalLoanSerializer
    filterset_fields = ['screening', 'lender_relationship']


class SpouseAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for spouse assessment with trust game"""
    queryset = SpouseAssessment.objects.all()
    serializer_class = SpouseAssessmentSerializer
    filterset_fields = ['screening', 'supports_loan', 'aware_of_debts']


class GuarantorAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for guarantor assessment with trust game"""
    queryset = GuarantorAssessment.objects.all()
    serializer_class = GuarantorAssessmentSerializer
    filterset_fields = ['screening', 'voluntary_guarantor', 'has_past_defaults']
    search_fields = ['full_name', 'relationship_to_client']


class HouseholdAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for household financial assessment"""
    queryset = HouseholdAssessment.objects.all()
    serializer_class = HouseholdAssessmentSerializer
    filterset_fields = ['screening']


class BusinessAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for business assessment"""
    queryset = BusinessAssessment.objects.all()
    serializer_class = BusinessAssessmentSerializer
    filterset_fields = ['screening', 'business_type']
    search_fields = ['business_name']


class BusinessItemViewSet(viewsets.ModelViewSet):
    """ViewSet for top business items"""
    queryset = BusinessItem.objects.all()
    serializer_class = BusinessItemSerializer
    filterset_fields = ['business']
    search_fields = ['item_name']


class ClientCollateralViewSet(viewsets.ModelViewSet):
    """ViewSet for client collateral"""
    queryset = ClientCollateral.objects.all()
    serializer_class = ClientCollateralSerializer
    filterset_fields = ['screening', 'collateral_type', 'physical_condition', 'ownership_verified']


class GuarantorCollateralViewSet(viewsets.ModelViewSet):
    """ViewSet for guarantor collateral"""
    queryset = GuarantorCollateral.objects.all()
    serializer_class = GuarantorCollateralSerializer
    filterset_fields = ['guarantor', 'collateral_type', 'physical_condition', 'ownership_verified']


class BehavioralVerificationViewSet(viewsets.ModelViewSet):
    """ViewSet for behavioral verification (proxy detection)"""
    queryset = BehavioralVerification.objects.all()
    serializer_class = BehavioralVerificationSerializer
    filterset_fields = ['screening', 'answered_by_proxy']