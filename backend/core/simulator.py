"""
Data simulator for Malawian credit risk application
Generates realistic loan data following all business rules
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
import pandas as pd

# Initialize Faker
fake = Faker()

# Malawian-specific data
MALAWIAN_FIRST_NAMES_MALE = [
    'Chisomo', 'Thoko', 'Kondwani', 'Mphatso', 'Limbani', 'Yamikani', 'Blessings',
    'Gift', 'Patrick', 'James', 'John', 'Peter', 'Moses', 'Isaac', 'David',
    'Samuel', 'Joseph', 'Daniel', 'Emmanuel', 'Francis', 'George', 'Henry'
]

MALAWIAN_FIRST_NAMES_FEMALE = [
    'Chisomo', 'Thoko', 'Mphatso', 'Alinafe', 'Chimwemwe', 'Tamanda', 'Thandiwe',
    'Grace', 'Mary', 'Ruth', 'Esther', 'Sarah', 'Rebecca', 'Rachel', 'Hannah',
    'Elizabeth', 'Martha', 'Joyce', 'Agnes', 'Catherine', 'Margaret', 'Lucy'
]

MALAWIAN_LAST_NAMES = [
    'Banda', 'Phiri', 'Mwale', 'Chirwa', 'Nyirenda', 'Tembo', 'Lungu', 'Sakala',
    'Mbewe', 'Zulu', 'Ng\'oma', 'Daka', 'Moyo', 'Kamoto', 'Gondwe', 'Kumwenda',
    'Mhango', 'Mvula', 'Kaunda', 'Chikwanda', 'Mhone', 'Soko', 'Nkhoma', 'Chulu'
]

DISTRICTS = [
    'Lilongwe', 'Blantyre', 'Mzuzu', 'Zomba', 'Kasungu', 'Mangochi', 'Salima',
    'Nkhotakota', 'Karonga', 'Mchinji', 'Dedza', 'Ntchisi', 'Dowa', 'Mzimba',
    'Rumphi', 'Chitipa', 'Mulanje', 'Thyolo', 'Chiradzulu', 'Phalombe', 'Nsanje',
    'Chikwawa', 'Balaka', 'Machinga', 'Neno'
]

TRADITIONAL_AUTHORITIES = {
    'Lilongwe': ['Chadza', 'Chitukula', 'Kalolo', 'Kalumba', 'Kaomba', 'Mazengera', 'Njewa'],
    'Kasungu': ['Chilowamatambe', 'Kaomba', 'Lukwa', 'Mwase', 'Njombwa', 'Santhe'],
    'Salima': ['Kalonga', 'Kambwiri', 'Khombedza', 'Maganga', 'Ndindi'],
    'Nkhotakota': ['Kanyenda', 'Malenga Chanzi', 'Malengachanzi', 'Mwadzama'],
    'Mzuzu': ['Mtwalo', 'Mzukuzuku', 'Jaravikuba', 'Kyungu'],
    'Blantyre': ['Kapeni', 'Kuntaja', 'Lundu', 'Machinjiri', 'Somba'],
    'Nsanje': ['Malemia', 'Mbenje', 'Ndamera', 'Ngabu', 'Nyachikadza'],
    'Mchinji': ['Dambe', 'Mkanda', 'Mlonyeni', 'Nyoka', 'Zulu'],
    'Karonga': ['Kilupula', 'Kyungu', 'Mwakaboko', 'Mwenewenya', 'Wasambo'],
}

VILLAGES = [
    'Chigoneka', 'Mpingu', 'Kaliyeka', 'Mtendere', 'Chinsapo', 'Kawale', 'Mchesi',
    'Kauma', 'Biwi', 'Chigodi', 'Mphomwa', 'Nkhoma', 'Chikuse', 'Mkanda'
]

COLLATERAL_DETAILS = {
    'BICYCLE': {
        'names': ['Hero Bicycle', 'Phoenix Bicycle', 'Atlas Bicycle', 'Raleigh Bicycle'],
        'values': (5000, 25000),
        'descriptions': ['Well-maintained bicycle', 'Used for transport', 'Good condition bicycle']
    },
    'MOTORBIKE': {
        'names': ['Honda Motorcycle', 'Yamaha Motorcycle', 'Bajaj Boxer', 'TVS Apache'],
        'values': (150000, 800000),
        'descriptions': ['Motorcycle for business', 'Transport motorcycle', 'Delivery motorcycle']
    },
    'LAND_CERTIFICATE': {
        'names': ['Residential Land Certificate', 'Agricultural Land Certificate', 'Customary Land Certificate'],
        'values': (200000, 2000000),
        'descriptions': ['Land in village', 'Agricultural plot', 'Residential plot']
    },
    'LIVESTOCK': {
        'names': ['Cattle (2 heads)', 'Goats (5 heads)', 'Pigs (3 heads)', 'Chickens (20 birds)'],
        'values': (50000, 500000),
        'descriptions': ['Livestock for farming', 'Animals for breeding', 'Poultry business']
    },
    'HOUSEHOLD_ITEMS': {
        'names': ['Furniture Set', 'Kitchen Appliances', 'Bedding and Furniture'],
        'values': (20000, 150000),
        'descriptions': ['Household furniture', 'Kitchen equipment', 'Home appliances']
    },
    'TV_RADIO': {
        'names': ['Flat Screen TV', 'Radio Set', 'TV and Sound System'],
        'values': (30000, 200000),
        'descriptions': ['Entertainment electronics', 'Television set', 'Audio equipment']
    },
    'FISHING_GEAR': {
        'names': ['Fishing Nets', 'Fishing Boat', 'Fishing Equipment Set'],
        'values': (40000, 400000),
        'descriptions': ['Commercial fishing nets', 'Fishing boat and nets', 'Complete fishing gear']
    },
    'VEHICLE': {
        'names': ['Toyota Corolla', 'Nissan March', 'Honda Fit', 'Mazda Demio'],
        'values': (800000, 3000000),
        'descriptions': ['Personal vehicle', 'Transport vehicle', 'Business vehicle']
    },
    'TITLE_DEED': {
        'names': ['Property Title Deed', 'House Title Deed', 'Commercial Property Deed'],
        'values': (500000, 5000000),
        'descriptions': ['Property ownership document', 'House title', 'Land title deed']
    },
    'STOCK': {
        'names': ['Shop Stock', 'Trading Stock', 'Business Inventory'],
        'values': (100000, 1000000),
        'descriptions': ['Retail shop inventory', 'Trading goods', 'Business stock']
    },
}


def generate_national_id():
    """Generate a fake Malawian national ID"""
    return f"MWI{random.randint(100000, 999999)}{random.choice(['A', 'B', 'C', 'D'])}"


def generate_employee_id():
    """Generate employee ID"""
    return f"EMP{random.randint(1000, 9999)}"


def generate_loan_number():
    """Generate unique loan number"""
    return f"LN{datetime.now().year}{random.randint(100000, 999999)}"


def generate_malawian_name(gender):
    """Generate Malawian name based on gender"""
    if gender == 'M':
        first_name = random.choice(MALAWIAN_FIRST_NAMES_MALE)
    else:
        first_name = random.choice(MALAWIAN_FIRST_NAMES_FEMALE)
    last_name = random.choice(MALAWIAN_LAST_NAMES)
    return first_name, last_name


def generate_location():
    """Generate location with district, T/A, and village"""
    district = random.choice(DISTRICTS)
    # Get T/A for district, or use a default if not in our mapping
    ta_list = TRADITIONAL_AUTHORITIES.get(district, ['Traditional Authority'])
    traditional_authority = random.choice(ta_list)
    village = random.choice(VILLAGES)
    return district, traditional_authority, village


def generate_income_by_industry(industry):
    """Generate realistic monthly income based on industry"""
    income_ranges = {
        'FARMING': (20000, 150000),
        'FISHING': (30000, 200000),
        'TRADING': (40000, 300000),
        'TRANSPORT': (50000, 400000),
        'CIVIL_SERVANT': (100000, 500000),
        'RETAIL': (35000, 250000),
        'CONSTRUCTION': (45000, 350000),
        'HOSPITALITY': (30000, 200000),
        'TAILORING': (25000, 180000),
        'CARPENTRY': (35000, 250000),
        'OTHER': (20000, 150000),
    }
    min_income, max_income = income_ranges.get(industry, (20000, 150000))
    return Decimal(str(random.randint(min_income, max_income)))


def generate_borrower_data(count=1000):
    """Generate borrower data"""
    borrowers = []
    industries = ['FARMING', 'FISHING', 'TRADING', 'TRANSPORT', 'CIVIL_SERVANT', 
                  'RETAIL', 'CONSTRUCTION', 'HOSPITALITY', 'TAILORING', 'CARPENTRY', 'OTHER']
    transport_modes = ['FOOT', 'BICYCLE', 'MOTORBIKE', 'CAR', 'MINIBUS']
    
    for i in range(count):
        gender = random.choice(['M', 'F'])
        first_name, last_name = generate_malawian_name(gender)
        district, ta, village = generate_location()
        industry = random.choice(industries)
        
        borrower = {
            'first_name': first_name,
            'last_name': last_name,
            'national_id': generate_national_id(),
            'date_of_birth': fake.date_of_birth(minimum_age=21, maximum_age=65),
            'gender': gender,
            'phone': f"+265{random.choice(['88', '99', '77'])}{random.randint(1000000, 9999999)}",
            'email': f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}" if random.random() > 0.3 else '',
            'village': village,
            'traditional_authority': ta,
            'district': district,
            'business_type': f"{industry.replace('_', ' ').title()} Business",
            'business_industry': industry,
            'monthly_income': generate_income_by_industry(industry),
            'transport_mode': random.choice(transport_modes),
        }
        borrowers.append(borrower)
    
    return borrowers


def generate_spouse_data(borrower, has_spouse_prob=0.6):
    """Generate spouse data for a borrower"""
    if random.random() > has_spouse_prob:
        return None
    
    # Spouse has opposite gender
    spouse_gender = 'F' if borrower['gender'] == 'M' else 'M'
    first_name, last_name = generate_malawian_name(spouse_gender)
    
    employment_statuses = ['EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED', 'STUDENT']
    employment = random.choice(employment_statuses)
    
    if employment == 'UNEMPLOYED' or employment == 'STUDENT':
        income = Decimal('0')
    else:
        income = Decimal(str(random.randint(15000, 250000)))
    
    spouse = {
        'first_name': first_name,
        'last_name': last_name,
        'age': random.randint(21, 60),
        'gender': spouse_gender,
        'employment_status': employment,
        'monthly_income': income,
        'relationship_start_date': fake.date_between(start_date='-20y', end_date='-1y'),
    }
    
    return spouse


def generate_guarantor_data(borrower, count=1):
    """Generate guarantor data"""
    guarantors = []
    relationships = ['PARENT', 'SIBLING', 'FRIEND', 'RELATIVE', 'BUSINESS_PARTNER', 'OTHER']
    employment_statuses = ['EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED', 'RETIRED']
    
    for _ in range(count):
        gender = random.choice(['M', 'F'])
        first_name, last_name = generate_malawian_name(gender)
        employment = random.choice(employment_statuses)
        
        if employment == 'UNEMPLOYED':
            income = Decimal('0')
        elif employment == 'RETIRED':
            income = Decimal(str(random.randint(30000, 150000)))
        else:
            income = Decimal(str(random.randint(40000, 400000)))
        
        guarantor = {
            'first_name': first_name,
            'last_name': last_name,
            'national_id': generate_national_id(),
            'age': random.randint(25, 70),
            'gender': gender,
            'relationship_to_borrower': random.choice(relationships),
            'employment_status': employment,
            'monthly_income': income,
            'phone': f"+265{random.choice(['88', '99', '77'])}{random.randint(1000000, 9999999)}",
            'collateral_backing': random.choice([True, False]),
        }
        guarantors.append(guarantor)
    
    return guarantors


def generate_loan_data(borrower, loan_type=None):
    """Generate loan data following business rules"""
    if loan_type is None:
        loan_type = random.choice(['BUSINESS', 'PAYDAY', 'YOUTH', 'WOMEN', 'MEN'])
    
    # Set interest rate based on loan type
    if loan_type == 'BUSINESS':
        monthly_interest_rate = Decimal(str(random.uniform(2.0, 5.0)))
    elif loan_type == 'PAYDAY':
        monthly_interest_rate = Decimal('33.0')
    elif loan_type == 'YOUTH':
        monthly_interest_rate = Decimal('3.0')
    elif loan_type == 'WOMEN':
        monthly_interest_rate = Decimal('2.5')
    elif loan_type == 'MEN':
        monthly_interest_rate = Decimal('4.0')
    
    # Set tenure
    if loan_type == 'PAYDAY':
        tenure_months = 1
        principal_amount = Decimal(str(random.randint(10000, 100000)))
    else:
        tenure_months = random.choice([4, 6, 9, 12, 15, 18, 24])
        principal_amount = Decimal(str(random.randint(50000, 2000000)))
    
    # Calculate disbursement fee (4%)
    disbursement_fee_rate = Decimal('4.0')
    disbursement_fee = principal_amount * (disbursement_fee_rate / 100)
    
    # Generate dates
    application_date = fake.date_between(start_date='-2y', end_date='today')
    approval_date = application_date + timedelta(days=random.randint(1, 14))
    disbursement_date = approval_date + timedelta(days=random.randint(1, 7))
    maturity_date = disbursement_date + timedelta(days=tenure_months * 30)
    
    # Status based on dates
    today = datetime.now().date()
    if disbursement_date > today:
        status = 'APPROVED'
    elif maturity_date < today:
        status = random.choices(['CLOSED', 'DEFAULTED', 'WRITTEN_OFF'], weights=[0.7, 0.2, 0.1])[0]
    else:
        status = 'ACTIVE'
    
    loan = {
        'loan_number': generate_loan_number(),
        'loan_type': loan_type,
        'principal_amount': principal_amount,
        'monthly_interest_rate': monthly_interest_rate,
        'disbursement_fee_rate': disbursement_fee_rate,
        'disbursement_fee': disbursement_fee,
        'tenure_months': tenure_months,
        'application_date': application_date,
        'approval_date': approval_date,
        'disbursement_date': disbursement_date,
        'maturity_date': maturity_date,
        'status': status,
    }
    
    return loan


def generate_collateral_data(loan, count=1):
    """Generate collateral data - no generic 'Other' allowed"""
    collaterals = []
    collateral_types = list(COLLATERAL_DETAILS.keys())
    
    for _ in range(count):
        collateral_type = random.choice(collateral_types)
        details = COLLATERAL_DETAILS[collateral_type]
        
        collateral_name = random.choice(details['names'])
        min_val, max_val = details['values']
        appraised_value = Decimal(str(random.randint(min_val, max_val)))
        market_value = appraised_value * Decimal(str(random.uniform(0.8, 1.2)))
        
        collateral = {
            'collateral_name': collateral_name,
            'collateral_type': collateral_type,
            'description': random.choice(details['descriptions']),
            'valuation_date': loan['disbursement_date'] - timedelta(days=random.randint(1, 30)),
            'appraised_value_mwk': appraised_value,
            'market_value_estimate_mwk': market_value,
            'condition': random.choices(['EXCELLENT', 'GOOD', 'FAIR', 'POOR'], weights=[0.2, 0.5, 0.25, 0.05])[0],
            'owner_type': random.choices(['BORROWER', 'SPOUSE', 'GUARANTOR'], weights=[0.7, 0.2, 0.1])[0],
        }
        collaterals.append(collateral)
    
    return collaterals


def generate_repayment_schedule(loan):
    """Generate repayment schedule and simulate actual payments"""
    repayments = []
    principal = loan['principal_amount']
    monthly_rate = loan['monthly_interest_rate'] / 100
    tenure = loan['tenure_months']
    
    # Calculate monthly payment (equal installments)
    if monthly_rate > 0:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** tenure) / ((1 + monthly_rate) ** tenure - 1)
    else:
        monthly_payment = principal / tenure
    
    current_date = loan['disbursement_date']
    remaining_principal = principal
    
    for i in range(1, tenure + 1):
        # Calculate scheduled payment
        scheduled_date = current_date + timedelta(days=30 * i)
        interest_payment = remaining_principal * monthly_rate
        principal_payment = monthly_payment - interest_payment
        
        if i == tenure:  # Last payment
            principal_payment = remaining_principal
            monthly_payment = principal_payment + interest_payment
        
        # Simulate actual payment
        payment_status, actual_date, actual_amount, days_late = simulate_payment(
            scheduled_date, monthly_payment, loan['status']
        )
        
        repayment = {
            'installment_number': i,
            'scheduled_date': scheduled_date,
            'scheduled_principal': principal_payment,
            'scheduled_interest': interest_payment,
            'scheduled_total': monthly_payment,
            'actual_payment_date': actual_date,
            'actual_amount_paid': actual_amount,
            'payment_status': payment_status,
            'days_late': days_late,
        }
        
        repayments.append(repayment)
        remaining_principal -= principal_payment
    
    return repayments


def simulate_payment(scheduled_date, scheduled_amount, loan_status):
    """Simulate actual payment with realistic delinquency patterns"""
    today = datetime.now().date()
    
    # If scheduled date is in the future, mark as scheduled
    if scheduled_date > today:
        return 'SCHEDULED', None, Decimal('0'), 0
    
    # Payment probabilities based on loan status
    if loan_status == 'CLOSED':
        # Closed loans have mostly on-time payments
        payment_type = random.choices(
            ['ON_TIME', 'LATE_PAYMENT', 'PARTIAL_PAYMENT'],
            weights=[0.8, 0.15, 0.05]
        )[0]
    elif loan_status == 'DEFAULTED' or loan_status == 'WRITTEN_OFF':
        # Defaulted loans have more missed and late payments
        payment_type = random.choices(
            ['ON_TIME', 'LATE_PAYMENT', 'PARTIAL_PAYMENT', 'MISSED_PAYMENT'],
            weights=[0.2, 0.3, 0.2, 0.3]
        )[0]
    else:  # ACTIVE
        payment_type = random.choices(
            ['ON_TIME', 'LATE_PAYMENT', 'PARTIAL_PAYMENT', 'MISSED_PAYMENT'],
            weights=[0.6, 0.2, 0.1, 0.1]
        )[0]
    
    if payment_type == 'ON_TIME':
        actual_date = scheduled_date + timedelta(days=random.randint(0, 3))
        actual_amount = scheduled_amount
        days_late = 0
    elif payment_type == 'LATE_PAYMENT':
        days_late = random.randint(4, 60)
        actual_date = scheduled_date + timedelta(days=days_late)
        actual_amount = scheduled_amount
    elif payment_type == 'PARTIAL_PAYMENT':
        days_late = random.randint(0, 30)
        actual_date = scheduled_date + timedelta(days=days_late)
        actual_amount = scheduled_amount * Decimal(str(random.uniform(0.3, 0.9)))
    else:  # MISSED_PAYMENT
        actual_date = None
        actual_amount = Decimal('0')
        days_late = (today - scheduled_date).days if today > scheduled_date else 0
    
    return payment_type, actual_date, actual_amount, days_late


# Export functions for use in Django management command
__all__ = [
    'generate_borrower_data',
    'generate_spouse_data',
    'generate_guarantor_data',
    'generate_loan_data',
    'generate_collateral_data',
    'generate_repayment_schedule',
]
