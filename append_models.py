"""
Script to append comprehensive screening models to models.py
"""

# Read current models.py
with open('backend/core/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any existing screening_models imports
lines = content.split('\n')
cleaned_lines = []
skip_next = False
for i, line in enumerate(lines):
    if 'screening_models' in line or (skip_next and not line.strip()):
        skip_next = 'screening_models' in line
        continue
    cleaned_lines.append(line)

# Write back cleaned content
with open('backend/core/models.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned_lines))

print("Cleaned models.py - removed screening_models imports")

# Now append comprehensive models
comprehensive_models = '''

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
'''

with open('backend/core/models.py', 'a', encoding='utf-8') as f:
    f.write(comprehensive_models)

print("Successfully appended comprehensive screening models to models.py")
