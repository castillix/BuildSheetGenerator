import report
import os

# Mock Data
specs = {
    'os_name': 'Windows 10 Pro',
    'is_laptop': True,
    'cpu_name': 'Intel Core i7-7600U',
    'cpu_cores': 2,
    'cpu_threads': 4,
    'ram_gb': 16,
    'ram_type': 'DDR4',
    'drives': [{'capacity_gb': 512, 'type': 'SSD'}],
    'gpu_name': 'Intel HD Graphics 620' # Integrated
}

price_data = {
    'final_price': 123.45, # This should be displayed if no override logic in generator (but here we pass data directly)
    # The generator logic in app.py handles the override BEFORE calling report.generate_pdf
    # So we just test that generate_pdf displays 'final_price' and NO breakdown list.
    'breakdown': {
        'base_fee': 40,
        'cpu_price': 150,
        'ram_price': 80,
        'drive_price': 50,
        'gpu_price': 0
    },
    'specs_used': {
        'year': 2017,
        'cores': 2,
        'threads': 4,
        'turbo': 3.9,
        'clock': 2800,
        'passmark': 6000
    }
}

custom_fields = {
    'computer_model': 'Dell Latitude 7480',
    'serial_number': 'OverrideTest',
    'builder_name': 'Test Builder',
    'features': {'wifi': True}
}

print("Generating PDF with Final Price 123.45...")
report.generate_pdf(specs, price_data, custom_fields, "Test_BuildSheet_PriceOverride.pdf")

print("PDF generated. Please check Test_BuildSheet_PriceOverride.pdf to confirm:")
print("1. Total Price is $123.45")
print("2. Price Breakdown list is ABSENT")
