import platform
import psutil
import json
import os
import sys

# Try to import wmi for Windows specific checks
try:
    import wmi
except ImportError:
    wmi = None

# Try to import cpuinfo
try:
    import cpuinfo
except ImportError:
    cpuinfo = None

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_system_info():
    """
    Scans the system for hardware info.
    Returns a dict with:
        - cpu_name
        - cpu_cores
        - cpu_threads
        - cpu_clock_max (approx)
        - ram_gb
        - ram_type (best effort)
        - drives: list of {device, mountpoint, fstype, opts, max_size_gb, type_guess}
        - gpu_name
        - os_name
        - is_laptop
    """
    info = {}
    
    # OS
    info['os_name'] = platform.system() + " " + platform.release()
    try:
        system = platform.system()
        if system == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                try:
                    display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                except FileNotFoundError:
                    display_version = None
                
                try:
                    release_id = winreg.QueryValueEx(key, "ReleaseId")[0]
                except FileNotFoundError:
                    release_id = None
                    
                try:
                    product_name = winreg.QueryValueEx(key, "ProductName")[0]
                except FileNotFoundError:
                    product_name = f"Windows {platform.release()}"

                # Check for Windows 11 (Build >= 22000)
                try:
                    current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                    if int(current_build) >= 22000:
                        product_name = product_name.replace("Windows 10", "Windows 11")
                except:
                    pass
                
                version = display_version if display_version else release_id
                if version:
                    info['os_name'] = f"{product_name} {version}"
                else:
                    info['os_name'] = product_name
            except:
                pass
                
        elif system == "Linux":
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    data = {}
                    for line in f:
                        if "=" in line:
                            k,v = line.strip().split("=", 1)
                            data[k] = v.strip('"')
                    
                    if "PRETTY_NAME" in data:
                        info['os_name'] = data["PRETTY_NAME"]
                    elif "NAME" in data and "VERSION" in data:
                        info['os_name'] = f"{data['NAME']} {data['VERSION']}"
        
        elif system == "Darwin": # macOS
            mac_ver = platform.mac_ver()[0]
            if mac_ver:
                info['os_name'] = f"macOS {mac_ver}"
            else:
                info['os_name'] = "macOS (Unknown Version)"
    except Exception as e:
        print(f"OS Detection Error: {e}")
    
    # CPU
    if cpuinfo:
        cpu_data = cpuinfo.get_cpu_info()
        info['cpu_name'] = cpu_data.get('brand_raw', platform.processor())
    else:
        info['cpu_name'] = platform.processor()
    
    info['cpu_cores'] = psutil.cpu_count(logical=False)
    info['cpu_threads'] = psutil.cpu_count(logical=True)
    
    # RAM
    svmem = psutil.virtual_memory()
    import math
    ram_gb_raw = svmem.total / (1024 ** 3)
    # Round up to nearest 2
    info['ram_gb'] = math.ceil(ram_gb_raw / 2) * 2
    
    # RAM Type - Hard to get cross-platform without sudo/special tools like dmidecode or wmi
    # Defaulting to DDR4 if unknown, or try WMI on Windows
    info['ram_type'] = "Unknown (Assume DDR4)" 
    if wmi:
        try:
            c = wmi.WMI()
            for mem in c.Win32_PhysicalMemory():
                # SMBIOS Memory Type
                # 20=DDR, 21=DDR2, 24=DDR3, 26=DDR4, 30=DDR5 (approx)
                mtype = mem.SMBIOSMemoryType
                if mtype == 24: info['ram_type'] = "DDR3"
                elif mtype == 26: info['ram_type'] = "DDR4"
                elif mtype >= 30: info['ram_type'] = "DDR5"
                elif mtype == 0: # Sometimes it is 0, check MemoryType?
                    pass
                break # Just check one stick for now
        except:
            pass

    # Storage
    drives = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        
        drive_type = "HDD/SSD" # psutil doesn't distinguish easily
        # On Windows, we can use WMI or PowerShell to check media type
        
        drives.append({
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "capacity_gb": round(partition_usage.total / (1024**3), 2),
            "type": drive_type 
        })
    info['drives'] = drives

    # Refine Drive Info on Windows
    if wmi:
        try:
            c = wmi.WMI()
            # Win32_DiskDrive might give MediaType
            for physical_disk in c.Win32_DiskDrive():
                # Map physical disk to info if possible, or just gather general types
                # Using MediaType often gives "Fixed hard disk media". 
                # "Model" often contains "SSD"
                pass
            
            # PowerShell is more reliable for MediaType: Get-PhysicalDisk | Select MediaType
            # We can run that and parse output if we want to be fancy.
            pass
        except:
            pass

    # GPU
    # Use WMI on Windows
    info['gpu_list'] = []
    
    if platform.system() == "Windows":
        if wmi:
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    if gpu.Name:
                        info['gpu_list'].append(gpu.Name)
            except:
                pass
        
        # Fallback/Additional check using PowerShell if WMI list is empty or for more details
        if not info['gpu_list']:
            try:
                import subprocess
                cmd = "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"
                result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    names = [n.strip() for n in result.stdout.split('\n') if n.strip()]
                    info['gpu_list'].extend(names)
            except:
                pass
                
    elif platform.system() == "Linux":
        try:
            import subprocess
            # Try lspci for GPU info
            result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "VGA compatible controller" in line or "3D controller" in line:
                        # Extract the part after the colon
                        parts = line.split(":", 2)
                        if len(parts) > 2:
                            info['gpu_list'].append(parts[2].strip())
        except:
            pass
            
    elif platform.system() == "Darwin": # macOS
        try:
            import subprocess
            result = subprocess.run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "Chipset Model:" in line:
                        info['gpu_list'].append(line.split(":", 1)[1].strip())
        except:
            pass

    # Deduplicate
    info['gpu_list'] = list(dict.fromkeys(info['gpu_list']))
    
    # Default gpu_name to the first one found
    if info['gpu_list']:
        info['gpu_name'] = info['gpu_list'][0]
    else:
        info['gpu_name'] = "Unknown"
    
    # Laptop detection (Battery check)
    battery = psutil.sensors_battery()
    info['is_laptop'] = battery is not None

    # Try to get serial number
    serial_number = "Unknown"
    try:
        if platform.system() == "Windows":
            # Method 1: Try WMI library (preferred)
            if wmi:
                try:
                    c = wmi.WMI()
                    for bios in c.Win32_BIOS():
                        if bios.SerialNumber and bios.SerialNumber.strip():
                            serial_number = bios.SerialNumber.strip()
                            break
                except Exception as e:
                    print(f"WMI method failed: {e}")
            
            # Method 2: PowerShell (Most reliable on modern Windows)
            if serial_number == "Unknown" or serial_number == "0":
                try:
                    import subprocess
                    cmd = "Get-CimInstance -ClassName Win32_BIOS | Select-Object -ExpandProperty SerialNumber"
                    result = subprocess.run(
                        ["powershell", "-Command", cmd],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    if result.returncode == 0:
                        sn = result.stdout.strip()
                        if sn and sn.upper() not in ['SERIALNUMBER', 'TO BE FILLED BY O.E.M.', '0']:
                            serial_number = sn
                except Exception as e:
                    print(f"PowerShell method failed: {e}")

            # Method 3: Fallback to wmic command (works without admin)
            if serial_number == "Unknown" or serial_number == "0":
                try:
                    import subprocess
                    result = subprocess.run(
                        ['wmic', 'bios', 'get', 'serialnumber'],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    if result.returncode == 0:
                        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                        # The first line is usually "SerialNumber", look for the value
                        if len(lines) > 1:
                            sn = lines[1]
                            if sn and sn.upper() not in ['SERIALNUMBER', 'TO BE FILLED BY O.E.M.', '0', 'NAME']:
                                serial_number = sn
                except Exception as e:
                    print(f"WMIC method failed: {e}")
                    
        elif platform.system() == "Linux":
            try:
                # Try dmidecode (requires root, may not work)
                import subprocess
                result = subprocess.run(['cat', '/sys/class/dmi/id/product_serial'], 
                                      capture_output=True, text=True, timeout=1)
                if result.returncode == 0 and result.stdout.strip():
                    serial_number = result.stdout.strip()
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                import subprocess
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Serial Number' in line:
                            serial_number = line.split(':')[-1].strip()
                            break
            except:
                pass
    except Exception as e:
        print(f"Serial number detection error: {e}")
    
    info['serial_number'] = serial_number
    
    return info

if __name__ == "__main__":
    print(json.dumps(get_system_info(), indent=4))
