import report
import pricing

# Mock Specs
specs = {
    'os_name': 'Windows 10 Pro 22H2',
    'is_laptop': True,
    'cpu_name': 'Intel Core i5-6500', 
    'cpu_cores': 4,
    'cpu_threads': 4,
    'ram_gb': 12,
    'ram_type': 'DDR4',
    'drives': [{'capacity_gb': 512, 'type': 'SSD'}],
    'gpu_name': 'Unknown'
}

# Test Pricing Rounding
print("Testing Price Rounding...")
p = pricing.calculate_price(specs)
print(f"Calculated Final Price: {p['final_price']} (Should be integer/rounded)")
if isinstance(p['final_price'], int):
    print("SUCCESS: Price is integer.")
elif p['final_price'].is_integer():
     print("SUCCESS: Price is rounded float.")
else:
    print(f"FAILURE: Price is not rounded: {p['final_price']}")

# Test PDF Generation
custom_fields = {'computer_model': 'Rounding Test', 'serial_number': '999', 'builder_name': 'Tester'}
print("\nGenerating PDF with Software Section...")
try:
    report.generate_pdf(specs, p, custom_fields, "Final_Round2_Test.pdf")
    print("PDF Generated: Final_Round2_Test.pdf. Check for 'Software Included' section.")
except Exception as e:
    print(f"PDF Generation FAILED: {e}")
