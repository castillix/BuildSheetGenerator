import report
import os

# Mock Data
specs = {
    'os_name': 'Windows 10',
    'is_laptop': True,
    'cpu_name': 'Test CPU',
    'cpu_cores': 4,
    'cpu_threads': 8,
    'ram_gb': 8,
    'ram_type': 'DDR4',
    'drives': [],
    'gpu_name': 'None'
}

price_data = {
    'final_price': 100,
    'discount_amount': 0,
    'breakdown': {},
    'specs_used': {}
}

# Case 1: Raw number
custom_fields_1 = {'screen_size': '15.6', 'computer_model': 'Test 1'}
report.generate_pdf(specs, price_data, custom_fields_1, "Test_Inches_1.pdf")

# Case 2: Already has inches
custom_fields_2 = {'screen_size': '14 Inches', 'computer_model': 'Test 2'}
report.generate_pdf(specs, price_data, custom_fields_2, "Test_Inches_2.pdf")

# Case 3: Has quote
custom_fields_3 = {'screen_size': '13.3"', 'computer_model': 'Test 3'}
report.generate_pdf(specs, price_data, custom_fields_3, "Test_Inches_3.pdf")

print("Generated 3 PDFs. Please check manually if needed, or assume success if no error.")
