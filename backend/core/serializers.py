"""
Django REST Framework serializers for all models
"""
from rest_framework import serializers
from .models import (
    Branch, LoanOfficer, Borrower, Spouse, Guarantor,
    Loan, Collateral, Repayment, Recovery,
    LoanRiskMetric, GroupRiskMetric, MacroMonthly,
    ClientScreening, HouseholdAssessment, BusinessAssessment, InformalLoan,
    SpouseAssessment, GuarantorAssessment, ClientProfile, BehavioralVerification,
    BusinessItem, ClientCollateral, GuarantorCollateral
)


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class LoanOfficerSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.get_name_display', read_only=True)
    
    class Meta:
        model = LoanOfficer
        fields = '__all__'


class SpouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spouse
        fields = '__all__'


class GuarantorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guarantor
        fields = '__all__'


class BorrowerSerializer(serializers.ModelSerializer):
    spouse = SpouseSerializer(read_only=True)
    guarantors = GuarantorSerializer(many=True, read_only=True)
    loan_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Borrower
        fields = '__all__'
    
    def get_loan_count(self, obj):
        return obj.loans.count()


class BorrowerListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    loan_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Borrower
        fields = ['id', 'first_name', 'last_name', 'national_id', 'district', 
                  'traditional_authority', 'business_industry', 'monthly_income', 
                  'gender', 'date_of_birth', 'loan_count']
    
    def get_loan_count(self, obj):
        return obj.loans.count()


class CollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collateral
        fields = '__all__'


class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = '__all__'


class RecoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recovery
        fields = '__all__'


class LoanRiskMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRiskMetric
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    borrower_name = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch.get_name_display', read_only=True)
    loan_officer_name = serializers.SerializerMethodField()
    collateral_items = CollateralSerializer(many=True, read_only=True)
    repayments = RepaymentSerializer(many=True, read_only=True)
    risk_metric = LoanRiskMetricSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = '__all__'
    
    def get_borrower_name(self, obj):
        return f"{obj.borrower.first_name} {obj.borrower.last_name}"
    
    def get_loan_officer_name(self, obj):
        return f"{obj.loan_officer.first_name} {obj.loan_officer.last_name}"


class LoanListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    borrower_name = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source='branch.get_name_display', read_only=True)
    
    class Meta:
        model = Loan
        fields = ['id', 'loan_number', 'borrower_name', 'branch_name', 'loan_type', 
                  'principal_amount', 'monthly_interest_rate', 'tenure_months', 
                  'disbursement_date', 'status']
    
    def get_borrower_name(self, obj):
        return f"{obj.borrower.first_name} {obj.borrower.last_name}"


class GroupRiskMetricSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.get_name_display', read_only=True)
    loan_type_display = serializers.CharField(source='get_loan_type_display', read_only=True)
    
    class Meta:
        model = GroupRiskMetric
        fields = '__all__'


class MacroMonthlySerializer(serializers.ModelSerializer):
    class Meta:
        model = MacroMonthly
        fields = '__all__'


# Statistics Serializers
class LoanStatisticsSerializer(serializers.Serializer):
    """Serializer for loan statistics"""
    total_loans = serializers.IntegerField()
    total_principal = serializers.DecimalField(max_digits=15, decimal_places=2)
    active_loans = serializers.IntegerField()
    defaulted_loans = serializers.IntegerField()
    avg_loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    by_loan_type = serializers.DictField()
    by_branch = serializers.DictField()


class RepaymentStatisticsSerializer(serializers.Serializer):
    """Serializer for repayment statistics"""
    total_repayments = serializers.IntegerField()
    on_time_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    partial_count = serializers.IntegerField()
    missed_count = serializers.IntegerField()
    on_time_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    avg_days_late = serializers.DecimalField(max_digits=8, decimal_places=2)


class PortfolioMetricsSerializer(serializers.Serializer):
    """Serializer for portfolio-level metrics"""
    par30_rate = serializers.DecimalField(max_digits=5, decimal_places=4)
    par60_rate = serializers.DecimalField(max_digits=5, decimal_places=4)
    par90_rate = serializers.DecimalField(max_digits=5, decimal_places=4)
    total_outstanding = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_at_risk_30 = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_at_risk_60 = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_at_risk_90 = serializers.DecimalField(max_digits=15, decimal_places=2)


class HouseholdAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdAssessment
        fields = '__all__'

class BusinessAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAssessment
        fields = '__all__'

class InformalLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformalLoan
        fields = '__all__'

class SpouseAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpouseAssessment
        fields = '__all__'
        read_only_fields = ['cooperation_score']

class GuarantorAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuarantorAssessment
        fields = '__all__'
        read_only_fields = ['trust_score']

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = '__all__'

class BehavioralVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehavioralVerification
        fields = '__all__'

class BusinessItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessItem
        fields = '__all__'

class ClientCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCollateral
        fields = '__all__'

class GuarantorCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuarantorCollateral
        fields = '__all__'

class ClientScreeningSerializer(serializers.ModelSerializer):
    household_assessment = HouseholdAssessmentSerializer(read_only=True)
    business_assessments = BusinessAssessmentSerializer(many=True, read_only=True)
    informal_loans = InformalLoanSerializer(many=True, read_only=True)
    spouse_assessment = SpouseAssessmentSerializer(read_only=True)
    guarantor_assessments = GuarantorAssessmentSerializer(many=True, read_only=True)
    client_profile = ClientProfileSerializer(read_only=True)
    behavioral_verification = BehavioralVerificationSerializer(read_only=True)
    borrower_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientScreening
        fields = '__all__'
        read_only_fields = ['client_risk_score', 'cluster_group', 'recommended_loan_amount', 'status', 'created_at', 'updated_at']

    def get_borrower_name(self, obj):
        return f"{obj.borrower.first_name} {obj.borrower.last_name}"
