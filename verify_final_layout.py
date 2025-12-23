import report
import os

specs = {
    'os_name': 'Windows 10 Pro 23H2',
    'is_laptop': False,
    'cpu_name': 'Intel Core i5-6500', 
    'cpu_cores': 4,
    'cpu_threads': 4,
    'ram_gb': 16,
    'ram_type': 'DDR4',
    'drives': [{'capacity_gb': 512, 'type': 'SSD'}],
    'gpu_name': 'Unknown'
}

price_data = {
    'final_price': 150.00,
    'breakdown': {'base_fee': 40, 'cpu_price': 50, 'ram_price': 40, 'drive_price': 20, 'gpu_price': 0, 'os_modifier': 0},
    'specs_used': {'year': 2016, 'cores': 4, 'threads': 4, 'turbo': 3.6, 'clock': 3200, 'passmark': 5600}
}
custom_fields = {'computer_model': 'Final Layout Test', 'serial_number': '12345', 'builder_name': 'Tester'}

print("Generating PDF...")
report.generate_pdf(specs, price_data, custom_fields, "Final_Layout_Test.pdf")
print("PDF Generated. Check 'Final_Layout_Test.pdf'.")
print("EXPECT FAILURES if layout logic is broken.")
