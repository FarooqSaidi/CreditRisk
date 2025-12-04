from django.contrib import admin
from .models import (
    Branch, LoanOfficer, Borrower, Spouse, Guarantor,
    Loan, Collateral, Repayment, Recovery,
    LoanRiskMetric, GroupRiskMetric, MacroMonthly
)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'created_at']
    search_fields = ['name', 'code']


@admin.register(LoanOfficer)
class LoanOfficerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'employee_id', 'branch', 'is_active']
    list_filter = ['branch', 'is_active']
    search_fields = ['first_name', 'last_name', 'employee_id']


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'national_id', 'district', 'traditional_authority', 'business_industry']
    list_filter = ['district', 'business_industry', 'gender']
    search_fields = ['first_name', 'last_name', 'national_id']


@admin.register(Spouse)
class SpouseAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'borrower', 'employment_status', 'monthly_income']
    list_filter = ['employment_status']
    search_fields = ['first_name', 'last_name']


@admin.register(Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'borrower', 'relationship_to_borrower', 'employment_status']
    list_filter = ['relationship_to_borrower', 'employment_status']
    search_fields = ['first_name', 'last_name', 'national_id']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_number', 'borrower', 'loan_type', 'principal_amount', 'status', 'disbursement_date']
    list_filter = ['loan_type', 'status', 'branch']
    search_fields = ['loan_number', 'borrower__first_name', 'borrower__last_name']
    date_hierarchy = 'disbursement_date'


@admin.register(Collateral)
class CollateralAdmin(admin.ModelAdmin):
    list_display = ['collateral_name', 'collateral_type', 'loan', 'appraised_value_mwk', 'condition']
    list_filter = ['collateral_type', 'condition', 'owner_type']
    search_fields = ['collateral_name', 'loan__loan_number']


@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'installment_number', 'scheduled_date', 'payment_status', 'days_late']
    list_filter = ['payment_status']
    search_fields = ['loan__loan_number']
    date_hierarchy = 'scheduled_date'


@admin.register(Recovery)
class RecoveryAdmin(admin.ModelAdmin):
    list_display = ['loan', 'recovery_date', 'recovery_amount', 'recovery_method']
    list_filter = ['recovery_method']
    search_fields = ['loan__loan_number']
    date_hierarchy = 'recovery_date'


@admin.register(LoanRiskMetric)
class LoanRiskMetricAdmin(admin.ModelAdmin):
    list_display = ['loan', 'pd_mean', 'lgd_mean', 'expected_loss', 'calculated_at']
    search_fields = ['loan__loan_number']


@admin.register(GroupRiskMetric)
class GroupRiskMetricAdmin(admin.ModelAdmin):
    list_display = ['branch', 'loan_type', 'tenure_months', 'mean_pd', 'mean_lgd', 'loan_count']
    list_filter = ['branch', 'loan_type']


@admin.register(MacroMonthly)
class MacroMonthlyAdmin(admin.ModelAdmin):
    list_display = ['month_date', 'gdp_growth_rate', 'inflation_rate', 'unemployment_rate']
    date_hierarchy = 'month_date'
