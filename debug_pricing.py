from pricing import load_prices_config, get_resource_path
import os
import sys

print("--- Debugging Pricing Config ---")
print(f"CWD: {os.getcwd()}")
if getattr(sys, 'frozen', False):
    print("Running in FROZEN mode")
    print(f"Exe Dir: {os.path.dirname(sys.executable)}")
else:
    print("Running in DEV mode")
    print(f"Script Dir: {os.path.dirname(os.path.abspath(__file__))}")

# Check where it looks
config = load_prices_config()
print(f"Loaded Config Keys: {list(config.keys())}")
print(f"BASE_FEE: {config.get('BASE_FEE')}")

# Manually check paths
res_path = get_resource_path('prices.txt')
print(f"Resource Path: {res_path} (Exists: {os.path.exists(res_path)})")

local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prices.txt')
print(f"Local Root Path: {local_path} (Exists: {os.path.exists(local_path)})")
