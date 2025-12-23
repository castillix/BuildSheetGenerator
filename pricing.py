import sqlite3
import math
import re
import difflib
import os

def get_resource_path(filename):
    """
    Get absolute path to resource, works for dev and frozen app
    """
    import sys
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, 'resources', filename)

def load_prices_config(config_path='prices.txt'):
    """
    Loads pricing configuration from a file.
    Returns a dict with key-value pairs.
    """
    config = {
        'BASE_FEE': 40.0,
        'RAM_DDR3_MULT': 1.5,
        'RAM_DDR4_MULT': 2.5,
        'RAM_DDR5_MULT': 6.0,
        'RAM_DEFAULT_MULT': 2.5,
        'DRIVE_HDD_PER_GB': 0.02,
        'DRIVE_SSD_PER_GB': 0.08,
        'DRIVE_NVME_PER_GB': 0.1,
        'DRIVE_DEFAULT_PER_GB': 0.08,
        'OS_LINUX_MULT': 0.85,
        'OS_MACOS_MULT': 1.2,
        'OS_WINDOWS_MULT': 1.0,
        'CPU_YEAR_BASE': 2012,
        'CPU_YEAR_LAPTOP_MULT': 6,
        'CPU_YEAR_DESKTOP_MULT': 10,
        'CPU_CORE_MULT': 0.025,
        'CPU_THREAD_EXCESS_PRICE': 0.75
    }
    
    # Resolve path if it's just a filename
    # User requested to always use current directory (CWD)
    # We do not try to resolve absolute paths relative to script/exe anymore.
    # config_path defaults to 'prices.txt' which will search CWD.
    
    loaded = False
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        try:
                            config[key] = float(value.strip())
                        except ValueError:
                            pass # Keep default if invalid
            loaded = True
        except Exception as e:
            print(f"Error loading prices.txt from {config_path}: {e}")
                
    # Debug logging
    try:
        log_path = "pricing_debug.txt"
        if getattr(sys, 'frozen', False):
             log_path = os.path.join(os.path.dirname(sys.executable), "pricing_debug.txt")
        
        with open(log_path, "w") as log:
            log.write(f"Loading prices from: {config_path}\n")
            log.write(f"File exists: {os.path.exists(config_path)}\n")
            if loaded:
                log.write(f"Loaded successfully. Keys: {list(config.keys())}\n")
                log.write(f"BASE_FEE: {config.get('BASE_FEE')}\n")
            else:
                log.write("Failed to load.\n")
    except Exception as e:
        pass

    if not loaded:
        print(f"Warning: {config_path} not found. Using internal defaults.")
            
    return config

def clean_cpu_name(name):
    """
    Cleans CPU name to improve matching success
    e.g. "Intel(R) Core(TM) i7-7600U CPU @ 2.80GHz" -> "Intel Core i7-7600U"
    """
    if not name: return ""
    # Remove (R), (TM), CPU, Processor
    name = re.sub(r'\(R\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\(TM\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+CPU\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+Processor\s*', '', name, flags=re.IGNORECASE)
    # Remove core/thread counts (e.g. 12-Core, 16-Thread)
    name = re.sub(r'\s+\d+-Core', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+\d+-Thread', '', name, flags=re.IGNORECASE)
    # Remove clock speed info if present (e.g. @ 2.80GHz)
    name = name.split('@')[0]
    # Remove extra spaces
    return " ".join(name.split())

def get_cpu_candidates(query, db_path='cpus.db', limit=20):
    """
    Finds potential CPU matches in the database.
    Returns list of dicts: {'name', 'year', 'cores', 'threads', 'clock', 'turbo', 'passmark', 'score'}
    """
    
    # Resolve db path
    if not os.path.isabs(db_path):
        res_path = get_resource_path(db_path)
        if os.path.exists(res_path):
            db_path = res_path
            
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    clean_query = clean_cpu_name(query)
    candidates = []
    
    # helper to add uniques
    seen_names = set()
    def add_candidates(rows, score_type):
        for row in rows:
            if row['name'] not in seen_names:
                d = dict(row)
                d['score'] = score_type
                candidates.append(d)
                seen_names.add(row['name'])

    # 1. Exact Match on Cleaned Name
    cursor.execute("SELECT * FROM cpus WHERE name = ?", (clean_query,))
    add_candidates(cursor.fetchall(), 100)
    
    # 2. LIKE Match (Start with)
    cursor.execute("SELECT * FROM cpus WHERE name LIKE ?", (f"{clean_query}%",))
    add_candidates(cursor.fetchall(), 90)
    
    # 3. LIKE Match (Contains)
    cursor.execute("SELECT * FROM cpus WHERE name LIKE ?", (f"%{clean_query}%",))
    add_candidates(cursor.fetchall(), 80)
    
    # 4. Token Match (More vague)
    # Split query into tokens, filter out common words like "Intel", "AMD", "Core" if we want, 
    # but for now just try to match significant parts.
    tokens = clean_query.split()
    significant_tokens = [t for t in tokens if len(t) > 2 and t.lower() not in ['intel', 'amd', 'core', 'ryzen', 'cpu']]
    
    if len(candidates) < limit and significant_tokens:
        # Try to match ANY of the significant tokens (OR logic) for broad search
        # Or AND logic for specific search. Let's try AND logic first with relaxed constraints.
        
        # Strategy: Match rows that contain ALL significant tokens
        if len(significant_tokens) > 0:
            query_parts = ["name LIKE ?" for _ in significant_tokens]
            sql = f"SELECT * FROM cpus WHERE {' AND '.join(query_parts)} LIMIT 50"
            params = [f"%{t}%" for t in significant_tokens]
            cursor.execute(sql, params)
            add_candidates(cursor.fetchall(), 60)
            
    # 5. Even more vague: Match ANY significant token (if still few results)
    if len(candidates) < 5 and significant_tokens:
         query_parts = ["name LIKE ?" for _ in significant_tokens]
         sql = f"SELECT * FROM cpus WHERE {' OR '.join(query_parts)} LIMIT 50"
         params = [f"%{t}%" for t in significant_tokens]
         cursor.execute(sql, params)
         add_candidates(cursor.fetchall(), 40)

    conn.close()
    
    return candidates[:limit]

def calculate_price(specs, db_path='cpus.db', manual_passmark=None):
    """
    Calculates the detailed price breakdown of the computer.
    
    specs: dict containing:
        - cpu_name: str (Raw string from scanner)
        - cpu_model_name: str (Optional: Specific DB name selected by user/logic)
        - ram_gb: float
        - ram_type: str ('DDR3', 'DDR4', 'DDR5')
        - drives: list of dicts [{'type': 'HDD'/'SSD'/'NVMe', 'capacity_gb': float}]
        - gpu_price: float (manual input)
        - os_name: str ('Windows', 'Linux', 'macOS')
        - is_laptop: bool
    
    manual_passmark: float (Optional override for passmark score)
    
    returns: dict with detailed price breakdown and total
    """
    
    # Resolve db path
    if not os.path.isabs(db_path):
        res_path = get_resource_path(db_path)
        if os.path.exists(res_path):
            db_path = res_path
    
    # Load Pricing Config
    prices = load_prices_config()
    
    # 1. Determine CPU details
    db_cpu = None
    
    # If a specific model name is provided (manual selection), try to load that exact one first
    if specs.get('cpu_model_name'):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM cpus WHERE name = ?", (specs['cpu_model_name'],))
        db_cpu = c.fetchone()
        conn.close()
    
    # If no specific model or not found, try search
    if not db_cpu:
        candidates = get_cpu_candidates(specs.get('cpu_name', ''), db_path)
        if candidates:
            db_cpu = candidates[0] # Best match
    
    # Unwrap CPU details
    if db_cpu:
        db_name = db_cpu['name']
        year = int(db_cpu['year']) if db_cpu['year'] else 2015
        cores = int(db_cpu['cores']) if db_cpu['cores'] else 2
        threads = int(db_cpu['threads']) if db_cpu['threads'] else 2
        clock = float(db_cpu['clock']) if db_cpu['clock'] else 2000
        turbo = float(db_cpu['turbo']) if db_cpu['turbo'] and db_cpu['turbo'] != -1 else clock
        passmark = float(db_cpu['passmark']) if db_cpu['passmark'] else 1000
    else:
        # Fallback / Not Found
        clean_name = clean_cpu_name(specs.get('cpu_name', 'Unknown'))
        # Only print warning if we don't have a manual passmark (which implies custom CPU or override)
        if not manual_passmark:
            print(f"Warning: CPU '{clean_name}' not found in DB. Using defaults.")
        db_name = clean_name + " (Not Found)"
        year, cores, threads, clock, turbo, passmark = 2015, 4, 4, 3000, 3500, 5000
        
        # If custom CPU fields are provided in specs (from manual entry mode)
        # We might want to use them, but usually they are passed via PDF generation.
        # Here we just calculate price. Manual passmark is separate.
        
    # Apply Manual Passmark if provided
    if manual_passmark is not None:
        try:
            passmark = float(manual_passmark)
        except (ValueError, TypeError):
            pass

    # Pricing Logic (Using Config)
    # double yearPrice = (build.cpu.year - 2012) * ((laptop) ? 6 : 10);
    laptop = specs.get('is_laptop', False)
    
    year_base = prices.get('CPU_YEAR_BASE', 2012)
    year_mult = prices.get('CPU_YEAR_LAPTOP_MULT', 6) if laptop else prices.get('CPU_YEAR_DESKTOP_MULT', 10)
    year_price = (year - year_base) * year_mult
    
    # double corePrice = build.cpu.cores * (yearPrice * 0.025);
    core_mult = prices.get('CPU_CORE_MULT', 0.025)
    core_price = cores * (year_price * core_mult)
    
    # double threadPrice = (build.cpu.threads - build.cpu.cores) * 0.75;
    thread_excess_price = prices.get('CPU_THREAD_EXCESS_PRICE', 0.75)
    thread_price = (threads - cores) * thread_excess_price
    
    # Turbo MUST be in GHz (e.g. 3.5).
    if turbo > 100: turbo = turbo / 1000.0
    
    # RAM Price
    ram_multiplier = prices.get('RAM_DEFAULT_MULT', 2.5)
    rtype = specs.get('ram_type', '').lower()
    if 'ddr3' in rtype: ram_multiplier = prices.get('RAM_DDR3_MULT', 1.5)
    elif 'ddr4' in rtype: ram_multiplier = prices.get('RAM_DDR4_MULT', 2.5)
    elif 'ddr5' in rtype: ram_multiplier = prices.get('RAM_DDR5_MULT', 6.0)
    
    ram_price = specs['ram_gb'] * ram_multiplier

    # Drive Price
    drive_price = 0
    for drive in specs['drives']:
        cap = drive['capacity_gb']
        dtype = drive['type'].lower()
        d_mult = prices.get('DRIVE_DEFAULT_PER_GB', 0.08)
        if 'hdd' in dtype: d_mult = prices.get('DRIVE_HDD_PER_GB', 0.02)
        elif 'nvme' in dtype: d_mult = prices.get('DRIVE_NVME_PER_GB', 0.1)
        elif 'ssd' in dtype: d_mult = prices.get('DRIVE_SSD_PER_GB', 0.08)
        drive_price += cap * d_mult

    gpu_price = specs.get('gpu_price', 0.0)

    # OS Modifier and Temp Calc
    temp = (((core_price + thread_price) * turbo) + year_price) + ram_price + drive_price + gpu_price
    
    os_modifier = 0
    os_name = specs['os_name'].lower()
    
    os_mult = prices.get('OS_WINDOWS_MULT', 1.0) # Default
    if 'linux' in os_name or 'ubuntu' in os_name or 'fedora' in os_name or 'debian' in os_name or 'pop' in os_name or 'mint' in os_name:
        os_mult = prices.get('OS_LINUX_MULT', 0.85)
    elif 'mac' in os_name or 'macos' in os_name:
        os_mult = prices.get('OS_MACOS_MULT', 1.2)
    elif 'windows' in os_name or 'microsoft' in os_name:
        os_mult = prices.get('OS_WINDOWS_MULT', 1.0)
        
    # Logic: modifier is the difference from temp
    # If os_mult is 0.85 (15% off), price is temp * 0.85. 
    # The "modifier" value added to breakdown is (temp * 0.85) - temp = negative number
    os_modifier = (os_mult * temp) - temp

    # double cpuPrice = (laptop) ?
    #         (((corePrice + threadPrice) * turbo) + yearPrice) * (passmark/5813) :
    #         (((corePrice + threadPrice) * turbo) + yearPrice) * ((passmark/9530) * 0.67);
    
    base_cpu_calc = ((core_price + thread_price) * turbo) + year_price
    
    if laptop:
        cpu_price = base_cpu_calc * (passmark / 5813.0)
    else:
        cpu_price = base_cpu_calc * ((passmark / 9530.0) * 0.67)

    # double finalPrice = (cpuPrice + ramPrice + drivePrice + gpuPrice + osModifier) + 40;
    base_fee = prices.get('BASE_FEE', 40.0)
    final_price = cpu_price + ram_price + drive_price + gpu_price + os_modifier + base_fee

    return {
        'final_price': round(final_price),
        'breakdown': {
            'cpu_model': db_name,
            'cpu_price': round(cpu_price),
            'ram_price': round(ram_price),
            'drive_price': round(drive_price),
            'gpu_price': round(gpu_price),
            'os_modifier': round(os_modifier),
            'base_fee': base_fee
        },
        'specs_used': {
            'year': year,
            'cores': cores,
            'threads': threads,
            'turbo': turbo,
            'clock': clock,
            'passmark': passmark
        }
    }
