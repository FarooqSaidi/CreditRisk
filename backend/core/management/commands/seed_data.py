"""
Django management command to seed the database with simulated loan data
Usage: python manage.py seed_data --count 10000
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    Branch, LoanOfficer, Borrower, Spouse, Guarantor,
    Loan, Collateral, Repayment
)
from core.simulator import (
    generate_borrower_data,
    generate_spouse_data,
    generate_guarantor_data,
    generate_loan_data,
    generate_collateral_data,
    generate_repayment_schedule,
    generate_employee_id,
)
import random
from datetime import datetime


class Command(BaseCommand):
    help = 'Seed database with simulated Malawian loan data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1000,
            help='Number of loans to generate (default: 1000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS(f'Starting data generation for {count} loans...'))

        # Create branches first
        branches = self.create_branches()
        self.stdout.write(self.style.SUCCESS(f'Created {len(branches)} branches'))

        # Create loan officers
        loan_officers = self.create_loan_officers(branches)
        self.stdout.write(self.style.SUCCESS(f'Created {len(loan_officers)} loan officers'))

        # Generate borrowers (fewer than loans since some borrowers have multiple loans)
        borrower_count = int(count * 0.7)  # 70% unique borrowers
        self.stdout.write(f'Generating {borrower_count} borrowers...')
        borrower_data_list = generate_borrower_data(borrower_count)

        # Create borrowers, spouses, guarantors, and loans
        self.stdout.write('Creating borrowers, loans, and related data...')
        self.create_all_data(borrower_data_list, branches, loan_officers, count)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded database with {count} loans!'))
        self.print_summary()

    def clear_data(self):
        """Clear all existing data"""
        Repayment.objects.all().delete()
        Collateral.objects.all().delete()
        Loan.objects.all().delete()
        Guarantor.objects.all().delete()
        Spouse.objects.all().delete()
        Borrower.objects.all().delete()
        LoanOfficer.objects.all().delete()
        Branch.objects.all().delete()

    def create_branches(self):
        """Create all Malawian branches"""
        branch_data = [
            ('LILONGWE', 'LLW'),
            ('KASUNGU', 'KSG'),
            ('SALIMA', 'SLM'),
            ('NKHOTAKOTA', 'NKK'),
            ('MZUZU', 'MZU'),
            ('BLANTYRE', 'BLT'),
            ('MSANJE', 'MSJ'),
            ('MCHINJI', 'MCH'),
            ('KARONGA', 'KRG'),
        ]

        branches = []
        for name, code in branch_data:
            branch, created = Branch.objects.get_or_create(
                name=name,
                defaults={
                    'code': code,
                    'address': f'{name.title()} District, Malawi',
                    'phone': f'+265{random.randint(1000000, 9999999)}'
                }
            )
            branches.append(branch)

        return branches

    def create_loan_officers(self, branches):
        """Create loan officers for each branch"""
        from core.simulator import generate_malawian_name
        from datetime import date, timedelta

        loan_officers = []
        officers_per_branch = 3

        for branch in branches:
            for i in range(officers_per_branch):
                gender = random.choice(['M', 'F'])
                first_name, last_name = generate_malawian_name(gender)

                officer = LoanOfficer.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    employee_id=generate_employee_id(),
                    branch=branch,
                    email=f'{first_name.lower()}.{last_name.lower()}@creditrisk.mw',
                    phone=f'+265{random.choice(["88", "99", "77"])}{random.randint(1000000, 9999999)}',
                    hire_date=date.today() - timedelta(days=random.randint(365, 3650)),
                    is_active=True
                )
                loan_officers.append(officer)

        return loan_officers

    @transaction.atomic
    def create_all_data(self, borrower_data_list, branches, loan_officers, target_loan_count):
        """Create all borrowers, loans, and related data"""
        loans_created = 0
        batch_size = 100

        borrowers_batch = []
        spouses_batch = []
        guarantors_batch = []
        loans_batch = []
        collaterals_batch = []
        repayments_batch = []

        for idx, borrower_data in enumerate(borrower_data_list):
            # Create borrower
            borrower = Borrower(**borrower_data)
            borrowers_batch.append(borrower)

            if len(borrowers_batch) >= batch_size or idx == len(borrower_data_list) - 1:
                Borrower.objects.bulk_create(borrowers_batch)
                created_borrowers = borrowers_batch.copy()
                borrowers_batch = []

                # Now create related data for these borrowers
                for borrower in created_borrowers:
                    # Create spouse (60% probability)
                    spouse_data = generate_spouse_data(borrower_data)
                    if spouse_data:
                        spouse = Spouse(borrower=borrower, **spouse_data)
                        spouses_batch.append(spouse)

                    # Create guarantors (1-2 per borrower)
                    guarantor_count = random.choice([1, 2])
                    guarantor_data_list = generate_guarantor_data(borrower_data, guarantor_count)
                    for guarantor_data in guarantor_data_list:
                        guarantor = Guarantor(borrower=borrower, **guarantor_data)
                        guarantors_batch.append(guarantor)

                    # Create loans (1-3 per borrower, but respect target count)
                    loans_for_borrower = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]

                    for _ in range(loans_for_borrower):
                        if loans_created >= target_loan_count:
                            break

                        # Generate loan
                        loan_data = generate_loan_data(borrower_data)
                        branch = random.choice(branches)
                        loan_officer = random.choice([lo for lo in loan_officers if lo.branch == branch])

                        loan = Loan(
                            borrower=borrower,
                            branch=branch,
                            loan_officer=loan_officer,
                            **loan_data
                        )
                        loans_batch.append(loan)
                        loans_created += 1

                        if loans_created % 100 == 0:
                            self.stdout.write(f'Generated {loans_created} loans...')

                    if loans_created >= target_loan_count:
                        break

                # Bulk create spouses and guarantors
                if spouses_batch:
                    Spouse.objects.bulk_create(spouses_batch)
                    spouses_batch = []

                if guarantors_batch:
                    Guarantor.objects.bulk_create(guarantors_batch)
                    guarantors_batch = []

                # Bulk create loans
                if loans_batch:
                    Loan.objects.bulk_create(loans_batch)
                    created_loans = loans_batch.copy()
                    loans_batch = []

                    # Create collateral and repayments for each loan
                    for loan in created_loans:
                        # Create collateral (1-2 items per loan)
                        collateral_count = random.choice([1, 2])
                        collateral_data_list = generate_collateral_data(loan_data, collateral_count)
                        for collateral_data in collateral_data_list:
                            collateral = Collateral(loan=loan, **collateral_data)
                            collaterals_batch.append(collateral)

                        # Create repayment schedule
                        repayment_data_list = generate_repayment_schedule(loan_data)
                        for repayment_data in repayment_data_list:
                            repayment = Repayment(loan=loan, **repayment_data)
                            repayments_batch.append(repayment)

                    # Bulk create collaterals and repayments
                    if collaterals_batch:
                        Collateral.objects.bulk_create(collaterals_batch)
                        collaterals_batch = []

                    if repayments_batch:
                        Repayment.objects.bulk_create(repayments_batch)
                        repayments_batch = []

            if loans_created >= target_loan_count:
                break

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write(self.style.SUCCESS('\n=== Database Summary ==='))
        self.stdout.write(f'Branches: {Branch.objects.count()}')
        self.stdout.write(f'Loan Officers: {LoanOfficer.objects.count()}')
        self.stdout.write(f'Borrowers: {Borrower.objects.count()}')
        self.stdout.write(f'Spouses: {Spouse.objects.count()}')
        self.stdout.write(f'Guarantors: {Guarantor.objects.count()}')
        self.stdout.write(f'Loans: {Loan.objects.count()}')
        self.stdout.write(f'Collateral Items: {Collateral.objects.count()}')
        self.stdout.write(f'Repayments: {Repayment.objects.count()}')

        # Loan type breakdown
        self.stdout.write(self.style.SUCCESS('\n=== Loan Type Breakdown ==='))
        for loan_type, display_name in Loan.LOAN_TYPE_CHOICES:
            count = Loan.objects.filter(loan_type=loan_type).count()
            self.stdout.write(f'{display_name}: {count}')

        # Branch breakdown
        self.stdout.write(self.style.SUCCESS('\n=== Branch Breakdown ==='))
        for branch in Branch.objects.all():
            count = Loan.objects.filter(branch=branch).count()
            self.stdout.write(f'{branch.get_name_display()}: {count} loans')
