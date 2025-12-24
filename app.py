from flask import Flask, render_template, request, jsonify, send_file
import scanner
import pricing
import report
import os
import json
import socket
import sys

if getattr(sys, 'frozen', False):
    # Running in a bundle
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    # Running in normal python environment
    app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_hardware():
    """Scan hardware and return specs as JSON"""
    try:
        specs = scanner.get_system_info()
        
        # Get CPU candidates using fuzzy search
        cpu_candidates = pricing.get_cpu_candidates(specs.get('cpu_name', ''))
        
        # Calculate initial pricing (uses best match by default)
        specs['gpu_price'] = 0.0  # Default GPU price
        
        # If we have candidates, use the first one as the specific model for initial calculation
        if cpu_candidates:
            specs['cpu_model_name'] = cpu_candidates[0]['name']
            
        price_data = pricing.calculate_price(specs)
        
        return jsonify({
            'success': True,
            'specs': specs,
            'cpu_candidates': cpu_candidates,
            'pricing': price_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search-cpu', methods=['POST'])
def search_cpu():
    """Search for CPU candidates by name/query"""
    try:
        data = request.json
        query = data.get('query', '')
        limit = data.get('limit', 20)
        
        candidates = pricing.get_cpu_candidates(query, limit=limit)
        
        return jsonify({
            'success': True,
            'candidates': candidates
        })
    except Exception as e:
         return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recalculate-price', methods=['POST'])
def recalculate_price():
    """Recalculate price based on updated specs (e.g. manual CPU selection)"""
    try:
        data = request.json
        specs = data.get('specs', {})
        manual_passmark = data.get('manual_passmark')
        
        # Ensure we have necessary fields
        if 'gpu_price' not in specs:
            specs['gpu_price'] = 0.0
            
        price_data = pricing.calculate_price(specs, manual_passmark=manual_passmark)
        
        return jsonify({
            'success': True,
            'pricing': price_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF with custom data"""
    try:
        data = request.json
        
        # Extract specs and custom fields
        specs = data.get('specs', {})
        manual_passmark = data.get('manual_passmark')
        
        custom_fields = {
            'computer_model': data.get('computer_model', ''),
            'serial_number': data.get('serial_number', ''),
            'builder_name': data.get('builder_name', ''),
            'notes': data.get('notes', ''),
            'discount_percent': float(data.get('discount_percent', 0)),
            'gpu_name': data.get('gpu_name', ''),
            'screen_size': data.get('screen_size', ''),
            'battery_health': data.get('battery_health', ''),
            'battery_duration': data.get('battery_duration', ''),
            'features': data.get('features', {}),
            'software_list': data.get('software_list', []),
            'custom_cpu': data.get('custom_cpu', None)
        }
        
        # Recalculate pricing with updated values
        include_gpu = data.get('include_gpu', True)
        specs['gpu_price'] = float(data.get('gpu_price', 0)) if include_gpu else 0.0
        price_data = pricing.calculate_price(specs, manual_passmark=manual_passmark)
        
        # Apply manual price overrides if provided
        price_overrides = data.get('price_overrides', {})
        if 'cpu_price' in price_overrides:
            price_data['breakdown']['cpu_price'] = float(price_overrides['cpu_price'])
        if 'ram_price' in price_overrides:
            price_data['breakdown']['ram_price'] = float(price_overrides['ram_price'])
        if 'drive_price' in price_overrides:
            price_data['breakdown']['drive_price'] = float(price_overrides['drive_price'])
            
        # Recalculate final price with overrides (unless explicitly overridden)
        bd = price_data['breakdown']
        
        if 'final_price' in price_overrides:
             price_data['final_price'] = float(price_overrides['final_price'])
        else:
             gpu_component = bd['gpu_price'] if include_gpu else 0.0
             price_data['final_price'] = (bd['base_fee'] + bd['cpu_price'] + bd['ram_price'] + 
                                          bd['drive_price'] + gpu_component + bd['os_modifier'])
        
        # Apply discount if specified
        if custom_fields['discount_percent'] > 0:
            discount_amount = price_data['final_price'] * (custom_fields['discount_percent'] / 100)
            price_data['discount_amount'] = discount_amount
            price_data['final_price'] -= discount_amount
        
        # Update custom fields with include_gpu for report.py
        custom_fields['include_gpu'] = include_gpu

        # Generate PDF
        pdf_path = report.generate_pdf(specs, price_data, custom_fields)
        
        # Open PDF automatically
        abs_path = os.path.abspath(pdf_path)
        try:
            if os.name == 'nt':  # Windows
                os.startfile(abs_path)
            elif os.uname().sysname == 'Darwin':  # macOS
                import subprocess
                subprocess.run(['open', abs_path])
            else:  # Linux and others
                import subprocess
                subprocess.run(['xdg-open', abs_path], check=False)
        except Exception as e:
            print(f"Could not open PDF automatically: {e}")
        
        return jsonify({
            'success': True,
            'pdf_path': os.path.abspath(pdf_path)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def find_available_port(start_port=8888, max_attempts=100):
    """Find the first available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts}")

if __name__ == '__main__':
    # Create necessary directories (only in dev mode)
    if not getattr(sys, 'frozen', False):
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static', exist_ok=True)
    
    try:
        # Check if we are running in the reloader subprocess
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            # We are in the reloader subprocess, use the port passed from parent
            port = int(os.environ.get('BUILD_SHEET_PORT', 8888))
            print(f" * Restarting with reloader, port: {port}")
        else:
            # We are in the main process
            port = find_available_port()
            os.environ['BUILD_SHEET_PORT'] = str(port)
            print("Starting Build Sheet Generator Web Interface...")
            print(f"Open your browser and navigate to: http://localhost:{port}")

        app.run(debug=True, port=port)
    except Exception as e:
        print(f"Error starting server: {e}")
