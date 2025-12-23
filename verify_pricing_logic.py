import pricing

# Test Cases
test_os_names = [
    "Windows 10",
    "Ubuntu 22.04",
    "Linux Mint 21",
    "Pop!_OS 22.04",
    "Fedora 36",
    "Debian GNU/Linux"
]

specs_template = {
    'cpu_name': 'Intel Core i5',
    'cpu_model_name': 'Intel Core i5-6500', # Mock match
    'ram_gb': 8,
    'ram_type': 'DDR4',
    'drives': [{'capacity_gb': 256, 'type': 'SSD'}],
    'gpu_price': 0,
    'is_laptop': False
}

print("Testing OS Modifier Logic:")
for os_name in test_os_names:
    test_specs = specs_template.copy()
    test_specs['os_name'] = os_name
    
    # Calculate
    price_data = pricing.calculate_price(test_specs)
    modifier = price_data['breakdown']['os_modifier']
    
    print(f"OS: {os_name: <20} | Modifier: {modifier}")

# Validate specifically Linux Mint (User's likely OS based on 'FreeGeek')
mint_specs = specs_template.copy()
mint_specs['os_name'] = "Linux Mint 21.1 Vera"
res = pricing.calculate_price(mint_specs)
print(f"\nSpecific Test 'Linux Mint 21.1 Vera': {res['breakdown']['os_modifier']}")
if res['breakdown']['os_modifier'] < 0:
    print("SUCCESS: Linux Mint detected as Linux (Negative Modifier)")
else:
    print("FAILURE: Linux Mint NOT detected (Modifier is 0)")
