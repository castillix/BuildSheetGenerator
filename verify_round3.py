import pricing
import report
import math

# Mock Specs
specs = {
     'os_name': 'Windows 10 Pro',
     'is_laptop': False,
     'cpu_name': 'Intel Core i5-6500', 
     'ram_gb': 16,
     'ram_type': 'DDR4',
     'drives': [{'capacity_gb': 1000, 'type': 'SSD'}],
     'gpu_name': 'NVIDIA GeForce GTX 1060'
}

print("--- Testing Pricing Rounding ---")
p = pricing.calculate_price(specs)
print(f"Final Price: {p['final_price']} (Type: {type(p['final_price'])})")
print("Breakdown:")
for k, v in p['breakdown'].items():
    if isinstance(v, (int, float)):
        print(f"  {k}: {v} (Type: {type(v)})")
        if not float(v).is_integer():
             print(f"  FAIL: {k} is not an integer!")

print("\n--- Generating PDF ---")
try:
    report.generate_pdf(specs, p, {'computer_model': 'Layout Test'}, "Final_Round3_LayoutTest.pdf")
    print("PDF Generated. Manually check 'Software Included' is inline and price is integer.")
except Exception as e:
    print(f"PDF Generation Failed: {e}")
