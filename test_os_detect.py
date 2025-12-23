import platform
import os
import sys

def get_better_os_info():
    system = platform.system()
    version = "Unknown"
    name = "Unknown"
    
    if system == "Windows":
        try:
            import winreg
            # Try to get DisplayVersion (20H2, 21H1, 22H2 etc)
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
            
            version = display_version if display_version else release_id
            name = product_name
            
            return f"{name} {version}"
        except Exception as e:
            return f"{platform.system()} {platform.release()} (Error: {e})"
            
    elif system == "Linux":
        try:
            # Check /etc/os-release
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    data = {}
                    for line in f:
                        if "=" in line:
                            k,v = line.strip().split("=", 1)
                            data[k] = v.strip('"')
                    
                    if "PRETTY_NAME" in data:
                        return data["PRETTY_NAME"]
                    elif "NAME" in data and "VERSION" in data:
                        return f"{data['NAME']} {data['VERSION']}"
        except:
            pass
            
    return f"{platform.system()} {platform.release()}"

print(f"Current Detection: {platform.system()} {platform.release()}")
print(f"Improved Detection: {get_better_os_info()}")
