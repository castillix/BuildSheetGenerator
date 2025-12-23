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
    'final_price': 350.50,
    'discount_amount': 0,
    'breakdown': {
        'base_fee': 40,
        'cpu_price': 150,
        'ram_price': 80,
        'drive_price': 50,
        'gpu_price': 0
    }
}

custom_fields = {
    'computer_model': 'Dell Latitude 7480',
    'serial_number': 'ABC123456',
    'builder_name': 'Test Builder',
    'notes': 'This is a test note to verify wrapping works correctly.',
    'features': {'wifi': True, 'bluetooth': True, 'webcam': True}
}

# 1. Test Standard Generation (Integrated GPU)
print("Generating standard PDF...")
report.generate_pdf(specs, price_data, custom_fields, "Test_BuildSheet_Standard.pdf")

# 2. Test Dedicated GPU
print("Generating dedicated GPU PDF...")
specs_gpu = specs.copy()
specs_gpu['gpu_name'] = 'NVIDIA GeForce GTX 1050'
price_data_gpu = price_data.copy()
price_data_gpu['breakdown']['gpu_price'] = 100
price_data_gpu['final_price'] = 450.50
custom_fields_gpu = custom_fields.copy()
custom_fields_gpu['gpu_name'] = 'NVIDIA GeForce GTX 1050'

report.generate_pdf(specs_gpu, price_data_gpu, custom_fields_gpu, "Test_BuildSheet_GPU.pdf")

print("PDFs generated. Please inspect file sizes.")
for f in ["Test_BuildSheet_Standard.pdf", "Test_BuildSheet_GPU.pdf"]:
    if os.path.exists(f):
        print(f" - {f}: {os.path.getsize(f)} bytes")
    else:
        print(f" - {f}: FAILED (Not found)")
