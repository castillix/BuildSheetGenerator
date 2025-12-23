import sys
import scanner
import pricing
import report
import os

def main():
    print("--- FreeGeek Build Sheet Generator ---")
    print("Scanning hardware...")
    
    try:
        specs = scanner.get_system_info()
    except Exception as e:
        print(f"Error scanning system: {e}")
        input("Press Enter to exit...")
        return

    print("\nDetected Specs:")
    print(f"CPU: {specs['cpu_name']}")
    print(f"RAM: {specs['ram_gb']} GB ({specs['ram_type']})")
    print(f"GPU: {specs['gpu_name']}")
    print(f"OS: {specs['os_name']}")
    
    # Manual Input for GPU Price (as requested)
    while True:
        try:
            val = input("\nEnter current market price for GPU ($): ")
            specs['gpu_price'] = float(val)
            break
        except ValueError:
            print("Invalid number. Please enter a value like '150.00'")

    # Pricing
    try:
        price_data = pricing.calculate_price(specs)
    except Exception as e:
        print(f"Error calculating price: {e}")
        # import traceback; traceback.print_exc()
        input("Press Enter to exit...")
        return

    print("\n--- Price Estimate ---")
    print(f"Total: ${price_data['final_price']:.2f}")
    
    # Report
    try:
        pdf_path = report.generate_pdf(specs, price_data)
        print(f"\nPDF Report generated: {os.path.abspath(pdf_path)}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
    
    input("\nPress Enter to finish...")

if __name__ == "__main__":
    main()
