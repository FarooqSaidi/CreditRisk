from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Branch(models.Model):
    """Fixed list of Malawian branches"""
    BRANCH_CHOICES = [
        ('LILONGWE', 'Lilongwe Branch'),
        ('KASUNGU', 'Kasungu Branch'),
        ('SALIMA', 'Salima Branch'),
        ('NKHOTAKOTA', 'Nkhotakota Branch'),
        ('MZUZU', 'Mzuzu Branch'),
        ('BLANTYRE', 'Blantyre Branch'),
        ('MSANJE', 'Msanje Branch'),
        ('MCHINJI', 'Mchinji Branch'),
        ('KARONGA', 'Karonga Branch'),
    ]
    
    name = models.CharField(max_length=50, choices=BRANCH_CHOICES, unique=True)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Branches"
    
    def __str__(self):
        return self.get_name_display()


class LoanOfficer(models.Model):
    """Staff managing loans"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='loan_officers')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"


class Borrower(models.Model):
    """Borrower with demographics and business information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    TRANSPORT_CHOICES = [
        ('FOOT', 'On Foot'),
        ('BICYCLE', 'Bicycle'),
        ('MOTORBIKE', 'Motorbike'),
        ('CAR', 'Car'),
        ('MINIBUS', 'Minibus'),
    ]
    
    INDUSTRY_CHOICES = [
        ('FARMING', 'Farming'),
        ('FISHING', 'Fishing'),
        ('TRADING', 'Trading'),
        ('TRANSPORT', 'Transport'),
        ('CIVIL_SERVANT', 'Civil Servant'),
        ('RETAIL', 'Retail'),
        ('CONSTRUCTION', 'Construction'),
        ('HOSPITALITY', 'Hospitality'),
        ('TAILORING', 'Tailoring'),
        ('CARPENTRY', 'Carpentry'),
        ('OTHER', 'Other'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Location Information
    village = models.CharField(max_length=100)
    traditional_authority = models.CharField(max_length=100)  # T/A - Mandatory
    district = models.CharField(max_length=100)
    
    # Business Information
    business_type = models.CharField(max_length=100)
    business_industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    # Transport
    transport_mode = models.CharField(max_length=20, choices=TRANSPORT_CHOICES)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"


class Spouse(models.Model):
    """Spouse information linked to borrower"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    EMPLOYMENT_CHOICES = [
        ('EMPLOYED', 'Employed'),
        ('SELF_EMPLOYED', 'Self-Employed'),
        ('UNEMPLOYED', 'Unemployed'),
        ('STUDENT', 'Student'),
    ]
    
    borrower = models.OneToOneField(Borrower, on_delete=models.CASCADE, related_name='spouse')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], default=0)
    relationship_start_date = models.DateField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (Spouse of {self.borrower.first_name})"


class Guarantor(models.Model):
    """Guarantor information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    EMPLOYMENT_CHOICES = [
        ('EMPLOYED', 'Employed'),
        ('SELF_EMPLOYED', 'Self-Employed'),
        ('UNEMPLOYED', 'Unemployed'),
        ('RETIRED', 'Retired'),
    ]
    
    RELATIONSHIP_CHOICES = [
        ('PARENT', 'Parent'),
        ('SIBLING', 'Sibling'),
        ('FRIEND', 'Friend'),
        ('RELATIVE', 'Relative'),
        ('BUSINESS_PARTNER', 'Business Partner'),
        ('OTHER', 'Other'),
    ]
    
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='guarantors')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    relationship_to_borrower = models.CharField(max_length=30, choices=RELATIONSHIP_CHOICES)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], default=0)
    phone = models.CharField(max_length=20)
    collateral_backing = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (Guarantor for {self.borrower.first_name})"


class Loan(models.Model):
    """Loan with business rules for interest rates and tenure"""
    LOAN_TYPE_CHOICES = [
        ('BUSINESS', 'Business Loan'),
        ('PAYDAY', 'PayDay Loan'),
        ('YOUTH', 'Youth Loan'),
        ('WOMEN', 'Women Loan'),
        ('MEN', 'Men Loan'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DISBURSED', 'Disbursed'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('DEFAULTED', 'Defaulted'),
        ('WRITTEN_OFF', 'Written Off'),
    ]
    
    # Loan Identification
    loan_number = models.CharField(max_length=20, unique=True)
    borrower = models.ForeignKey(Borrower, on_delete=models.PROTECT, related_name='loans')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='loans')
    loan_officer = models.ForeignKey(LoanOfficer, on_delete=models.PROTECT, related_name='loans')
    
    # Loan Details
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    monthly_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))])
    disbursement_fee_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('4.0'))  # 4% fee
    disbursement_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tenure_months = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(24)])
    
    # Dates
    application_date = models.DateField()
    approval_date = models.DateField(null=True, blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-set interest rate based on loan type
        if not self.monthly_interest_rate or self.monthly_interest_rate == 0:
            if self.loan_type == 'PAYDAY':
                self.monthly_interest_rate = Decimal('33.0')
            elif self.loan_type == 'YOUTH':
                self.monthly_interest_rate = Decimal('3.0')
            elif self.loan_type == 'WOMEN':
                self.monthly_interest_rate = Decimal('2.5')
            elif self.loan_type == 'MEN':
                self.monthly_interest_rate = Decimal('4.0')
            # BUSINESS loan rate is set randomly between 2-5% in simulator
        
        # Calculate disbursement fee
        self.disbursement_fee = self.principal_amount * (self.disbursement_fee_rate / 100)
        
        # Validate tenure for PayDay loans
        if self.loan_type == 'PAYDAY' and self.tenure_months != 1:
            raise ValueError("PayDay loans must have 1 month tenure")
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.loan_number} - {self.borrower.first_name} {self.borrower.last_name}"


class Collateral(models.Model):
    """Collateral with rich characteristics"""
    COLLATERAL_TYPE_CHOICES = [
        ('BICYCLE', 'Bicycle'),
        ('MOTORBIKE', 'Motorbike'),
        ('LAND_CERTIFICATE', 'Land Certificate'),
        ('LIVESTOCK', 'Livestock'),
        ('HOUSEHOLD_ITEMS', 'Household Items'),
        ('TV_RADIO', 'TV/Radio'),
        ('FISHING_GEAR', 'Fishing Gear'),
        ('VEHICLE', 'Vehicle'),
        ('TITLE_DEED', 'Title Deed'),
        ('STOCK', 'Stock'),
    ]
    
    CONDITION_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
    ]
    
    OWNER_TYPE_CHOICES = [
        ('BORROWER', 'Borrower'),
        ('SPOUSE', 'Spouse'),
        ('GUARANTOR', 'Guarantor'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='collateral_items')
    collateral_name = models.CharField(max_length=200)
    collateral_type = models.CharField(max_length=30, choices=COLLATERAL_TYPE_CHOICES)
    description = models.TextField()
    valuation_date = models.DateField()
    appraised_value_mwk = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    market_value_estimate_mwk = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    owner_type = models.CharField(max_length=20, choices=OWNER_TYPE_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Collateral"
    
    def __str__(self):
        return f"{self.collateral_name} ({self.collateral_type}) - {self.loan.loan_number}"


class Repayment(models.Model):
    """Repayment schedule and actual payments"""
    PAYMENT_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ON_TIME', 'On Time'),
        ('LATE_PAYMENT', 'Late Payment'),
        ('PARTIAL_PAYMENT', 'Partial Payment'),
        ('MISSED_PAYMENT', 'Missed Payment'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    installment_number = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Scheduled
    scheduled_date = models.DateField()
    scheduled_principal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    scheduled_interest = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    scheduled_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    # Actual
    actual_payment_date = models.DateField(null=True, blank=True)
    actual_amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='SCHEDULED')
    days_late = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['loan', 'installment_number']
        unique_together = ['loan', 'installment_number']
    
    def __str__(self):
        return f"{self.loan.loan_number} - Installment {self.installment_number}"


class Recovery(models.Model):
    """Post-default recovery tracking"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='recoveries')
    recovery_date = models.DateField()
    recovery_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    recovery_method = models.CharField(max_length=100)  # e.g., "Collateral Sale", "Legal Action", "Voluntary Payment"
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recovery for {self.loan.loan_number} - MWK {self.recovery_amount}"


class LoanRiskMetric(models.Model):
    """Loan-level risk metrics with Bayesian credible intervals"""
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='risk_metric')
    
    # Probability of Default (PD)
    pd_mean = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    pd_lower_hdi = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    pd_upper_hdi = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    
    # Loss Given Default (LGD)
    lgd_mean = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    lgd_lower_hdi = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    lgd_upper_hdi = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    
    # Exposure at Default (EAD)
    ead = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    # Expected Loss
    expected_loss = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    # Hazard Rate
    hazard_rate = models.DecimalField(max_digits=8, decimal_places=6, validators=[MinValueValidator(Decimal('0'))], null=True, blank=True)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Risk Metrics for {self.loan.loan_number}"


class GroupRiskMetric(models.Model):
    """Aggregated risk metrics by branch, loan product, and tenure"""
    # Grouping dimensions
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='risk_metrics', null=True, blank=True)
    loan_type = models.CharField(max_length=20, choices=Loan.LOAN_TYPE_CHOICES, null=True, blank=True)
    tenure_months = models.IntegerField(null=True, blank=True)
    
    # Aggregated PD
    mean_pd = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    
    # Aggregated LGD
    mean_lgd = models.DecimalField(max_digits=5, decimal_places=4, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))])
    
    # Aggregated EAD
    total_ead = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    # Expected Loss
    total_expected_loss = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    
    # Portfolio Metrics
    par30_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)  # Portfolio at Risk > 30 days
    par60_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    par90_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    
    # Recovery Rate
    recovery_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    
    # Sample size
    loan_count = models.IntegerField(default=0)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Group Risk Metrics"
    
    def __str__(self):
        parts = []
        if self.branch:
            parts.append(str(self.branch))
        if self.loan_type:
            parts.append(self.get_loan_type_display())
        if self.tenure_months:
            parts.append(f"{self.tenure_months}mo")
        return f"Group Metrics: {' - '.join(parts) if parts else 'Overall'}"


class MacroMonthly(models.Model):
    """Monthly macroeconomic indicators for Malawi"""
    month_date = models.DateField(unique=True)
    gdp_growth_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    inflation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    unemployment_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    exchange_rate_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    interest_rate_policy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Macro Monthly Data"
        ordering = ['-month_date']
    
    def __str__(self):
        return f"Macro Data - {self.month_date.strftime('%Y-%m')}"



# Import comprehensive screening models

# ============================================================================
# COMPREHENSIVE CLIENT SCREENING MODELS
# ============================================================================

class ClientScreening(models.Model):
    """Main container for comprehensive client screening"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('COMPLETED', 'Completed'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    RISK_CLUSTER_CHOICES = [
        ('LOW', 'Low Risk - Accept'),
        ('MEDIUM', 'Medium Risk - Conditional'),
        ('HIGH', 'High Risk - Reject'),
    ]

    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='comprehensive_screenings')
    screening_date = models.DateField(auto_now_add=True)
    
    # Loan Intention
    loan_usage_intention = models.TextField()
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    spouse_recommended_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    guarantor_recommended_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Risk Profile
    past_defaults = models.BooleanField(default=False)
    client_risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cluster_group = models.CharField(max_length=10, choices=RISK_CLUSTER_CHOICES, null=True, blank=True)
    recommended_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    loan_ratio = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Screening: {self.borrower} - {self.screening_date}"


class ClientProfile(models.Model):
    """Extended client info with identity verification"""
    EDUCATION_CHOICES = [
        ('NONE', 'No Formal Education'),
        ('PRIMARY', 'Primary'),
        ('SECONDARY', 'Secondary'),
        ('TERTIARY', 'Tertiary'),
    ]
    
    RESIDENCE_CHOICES = [
        ('OWNED', 'Owned'),
        ('RENTED', 'Rented'),
        ('TEMPORARY', 'Temporary'),
        ('RELATIVE', 'Living with Relative'),
    ]
    
    ID_TYPE_CHOICES = [
        ('NATIONAL_ID', 'National ID'),
        ('PASSPORT', 'Passport'),
        ('VOTER_CARD', 'Voter Card'),
    ]
    
    screening = models.OneToOneField(ClientScreening, on_delete=models.CASCADE, related_name='client_profile')
    
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    residence_type = models.CharField(max_length=20, choices=RESIDENCE_CHOICES)
    months_at_residence = models.IntegerField(validators=[MinValueValidator(0)])
    number_of_dependents = models.IntegerField(validators=[MinValueValidator(0)])
    number_of_active_businesses = models.IntegerField(validators=[MinValueValidator(1)])
    
    photo = models.ImageField(upload_to='client_photos/', null=True, blank=True)
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES)
    id_number = models.CharField(max_length=50)
    home_visit_conducted = models.BooleanField(default=False)
    proxy_applicant_detected = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Profile: {self.screening.borrower}"


class InformalLoan(models.Model):
    """Informal obligations with cross-verification"""
    screening = models.ForeignKey(ClientScreening, on_delete=models.CASCADE, related_name='informal_loans')
    
    lender_name = models.CharField(max_length=100)
    lender_relationship = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    repayment_schedule = models.CharField(max_length=100)
    
    spouse_verified = models.BooleanField(default=False)
    guarantor_verified = models.BooleanField(default=False)
    community_verified = models.BooleanField(default=False)
    
    receipt_upload = models.FileField(upload_to='informal_loan_receipts/', null=True, blank=True)
    
    def __str__(self):
        return f"Informal Loan: {self.lender_name} - MWK {self.amount}"


class SpouseAssessment(models.Model):
    """Spouse info with trust game"""
    INVOLVEMENT_CHOICES = [
        ('NONE', 'None'),
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    DECISION_POWER_CHOICES = [
        ('NONE', 'None'),
        ('PARTIAL', 'Partial'),
        ('FULL', 'Full'),
    ]
    
    screening = models.OneToOneField(ClientScreening, on_delete=models.CASCADE, related_name='spouse_assessment')
    
    full_name = models.CharField(max_length=200)
    supports_loan = models.BooleanField()
    aware_of_debts = models.BooleanField()
    financial_involvement = models.CharField(max_length=10, choices=INVOLVEMENT_CHOICES)
    decision_making_power = models.CharField(max_length=10, choices=DECISION_POWER_CHOICES)
    
    # Trust Game Questions
    q_support_repayment = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q_intervene_if_missed = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    
    # Auto-computed
    cooperation_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-compute cooperation score
        support_points = (self.q_support_repayment / 4) * 60
        intervene_points = (self.q_intervene_if_missed / 3) * 40
        self.cooperation_score = Decimal(str(support_points + intervene_points))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Spouse: {self.full_name}"


class GuarantorAssessment(models.Model):
    """Guarantor info with trust game"""
    screening = models.ForeignKey(ClientScreening, on_delete=models.CASCADE, related_name='guarantor_assessments')
    
    full_name = models.CharField(max_length=200)
    relationship_to_client = models.CharField(max_length=100)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    liquid_assets = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    voluntary_guarantor = models.BooleanField()
    has_past_defaults = models.BooleanField(default=False)
    
    # Trust Game Questions
    q_willingness_to_repay = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    q_aware_of_debts = models.BooleanField()
    q_incentive_alignment = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2)])
    q_past_reliability = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2)])
    
    # Auto-computed
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-compute trust score
        willingness = (self.q_willingness_to_repay / 4) * 40
        awareness = 20 if self.q_aware_of_debts else 0
        incentive = (self.q_incentive_alignment / 2) * 20
        reliability = (self.q_past_reliability / 2) * 20
        self.trust_score = Decimal(str(willingness + awareness + incentive + reliability))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Guarantor: {self.full_name}"


class GuarantorCollateral(models.Model):
    """Guarantor collateral with photo/GPS"""
    COLLATERAL_TYPE_CHOICES = [
        ('LAND', 'Land'),
        ('VEHICLE', 'Vehicle'),
        ('EQUIPMENT', 'Equipment'),
        ('STOCK', 'Stock/Inventory'),
        ('OTHER', 'Other'),
    ]
    
    CONDITION_CHOICES = [
        ('POOR', 'Poor'),
        ('FAIR', 'Fair'),
        ('GOOD', 'Good'),
        ('EXCELLENT', 'Excellent'),
    ]
    
    SEIZURE_DIFFICULTY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    guarantor = models.ForeignKey(GuarantorAssessment, on_delete=models.CASCADE, related_name='collaterals')
    
    collateral_type = models.CharField(max_length=20, choices=COLLATERAL_TYPE_CHOICES)
    description = models.TextField()
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    ownership_verified = models.BooleanField(default=False)
    physical_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    seizure_difficulty = models.CharField(max_length=10, choices=SEIZURE_DIFFICULTY_CHOICES)
    
    document_upload = models.FileField(upload_to='guarantor_collateral_docs/', null=True, blank=True)
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    def __str__(self):
        return f"{self.collateral_type} - {self.guarantor.full_name}"


class ClientCollateral(models.Model):
    """Client collateral with photo/GPS"""
    COLLATERAL_TYPE_CHOICES = [
        ('LAND', 'Land'),
        ('VEHICLE', 'Vehicle'),
        ('EQUIPMENT', 'Equipment'),
        ('STOCK', 'Stock/Inventory'),
        ('OTHER', 'Other'),
    ]
    
    CONDITION_CHOICES = [
        ('POOR', 'Poor'),
        ('FAIR', 'Fair'),
        ('GOOD', 'Good'),
        ('EXCELLENT', 'Excellent'),
    ]
    
    SEIZURE_DIFFICULTY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    screening = models.ForeignKey(ClientScreening, on_delete=models.CASCADE, related_name='client_collaterals')
    
    collateral_type = models.CharField(max_length=20, choices=COLLATERAL_TYPE_CHOICES)
    description = models.TextField()
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    ownership_verified = models.BooleanField(default=False)
    physical_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    seizure_difficulty = models.CharField(max_length=10, choices=SEIZURE_DIFFICULTY_CHOICES)
    
    photo_upload = models.ImageField(upload_to='client_collateral_photos/', null=True, blank=True)
    document_upload = models.FileField(upload_to='client_collateral_docs/', null=True, blank=True)
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    def __str__(self):
        return f"{self.collateral_type} - {self.screening.borrower}"


class HouseholdAssessment(models.Model):
    """Household financial assessment"""
    screening = models.OneToOneField(ClientScreening, on_delete=models.CASCADE, related_name='household_assessment')
    
    total_monthly_income = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    total_monthly_expenses = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    # Auto-computed
    net_monthly_cashflow = models.DecimalField(max_digits=12, decimal_places=2)
    
    liquid_assets = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    household_stability_years = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0'))])
    potential_shocks_discussed = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-compute net cashflow
        self.net_monthly_cashflow = self.total_monthly_income - self.total_monthly_expenses
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Household: {self.screening.borrower}"


class BusinessAssessment(models.Model):
    """Detailed business assessment"""
    BUSINESS_TYPE_CHOICES = [
        ('TRADE', 'Trade'),
        ('SERVICES', 'Services'),
        ('AGRICULTURE', 'Agriculture'),
        ('MANUFACTURING', 'Manufacturing'),
        ('OTHER', 'Other'),
    ]
    
    screening = models.ForeignKey(ClientScreening, on_delete=models.CASCADE, related_name='business_assessments')
    
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    business_age_years = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0'))])
    number_of_employees = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    number_of_outlets = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    seasonality_index = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    monthly_revenue = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    monthly_costs = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    # Auto-computed
    monthly_profit = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Detailed operational costs
    monthly_salaries = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_utilities = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    daily_selling_tax = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    daily_transport_home_to_shop = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monthly_transport_to_supplier = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    daily_food_at_shop = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monthly_food_supplier_trips = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    business_photo = models.ImageField(upload_to='business_photos/', null=True, blank=True)
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-compute profit
        self.monthly_profit = self.monthly_revenue - self.monthly_costs
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.business_name}"


class BusinessItem(models.Model):
    """Top 3 items per business"""
    business = models.ForeignKey(BusinessAssessment, on_delete=models.CASCADE, related_name='top_items')
    
    item_name = models.CharField(max_length=200)
    quantity_sold_per_month = models.IntegerField(validators=[MinValueValidator(0)])
    selling_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    buying_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    current_stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.item_name} - {self.business.business_name}"


class BehavioralVerification(models.Model):
    """Behavioral questions for proxy detection"""
    screening = models.OneToOneField(ClientScreening, on_delete=models.CASCADE, related_name='behavioral_verification')
    
    daily_cashflow_answer = models.TextField()
    key_suppliers_answer = models.TextField()
    key_clients_answer = models.TextField()
    business_routine_answer = models.TextField()
    
    answered_by_proxy = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Behavioral: {self.screening.borrower}"
