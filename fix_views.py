"""
Script to fix views.py by removing old screening imports
"""

with open('backend/core/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove the import block (lines 12-27)
new_lines = []
skip_mode = False
for i, line in enumerate(lines):
    line_num = i + 1
    
    # Start skipping at line 12
    if line_num == 12 and 'from .models import' in line:
        skip_mode = True
        # Add back just the models we need
        new_lines.append('from .models import (\n')
        new_lines.append('    Branch, LoanOfficer, Borrower, Spouse, Guarantor,\n')
        new_lines.append('    Loan, Collateral, Repayment, Recovery,\n')
        new_lines.append('    LoanRiskMetric, GroupRiskMetric, MacroMonthly\n')
        new_lines.append(')\n')
        continue
    
    # Skip until we hit the serializers import
    if skip_mode and 'from .serializers import' in line:
        new_lines.append('from .serializers import (\n')
        new_lines.append('    BranchSerializer, LoanOfficerSerializer, BorrowerSerializer, BorrowerListSerializer,\n')
        new_lines.append('    SpouseSerializer, GuarantorSerializer, LoanSerializer, LoanListSerializer,\n')
        new_lines.append('    CollateralSerializer, RepaymentSerializer, RecoverySerializer,\n')
        new_lines.append('    LoanRiskMetricSerializer, GroupRiskMetricSerializer, MacroMonthlySerializer,\n')
        new_lines.append('    LoanStatisticsSerializer, RepaymentStatisticsSerializer, PortfolioMetricsSerializer\n')
        new_lines.append(')\n')
        skip_mode = False
        continue
    
    # Skip clustering import
    if 'from .clustering import' in line:
        continue
    
    # Skip lines in skip mode
    if skip_mode:
        continue
    
    new_lines.append(line)

# Write back
with open('backend/core/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed views.py - removed old screening imports")
