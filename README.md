# FreeGeek Build Sheet Generator

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Portable](https://img.shields.io/badge/portable-USB%20ready-brightgreen)

A **fully portable** web-based application for automatically scanning hardware specifications, calculating prices, and generating professional PDF build sheets for computer systems at FreeGeek.

## ✨ Key Features

- 🔌 **100% Portable** - Run directly from USB drive, no installation needed
- 🖥️ **Cross-Platform** - Works on Windows, Linux, and macOS
- 🚀 **One-Click Launch** - Just run the script for your platform
- 💾 **Pre-Configured** - All dependencies included in venv
- 📊 **Smart Hardware Detection** - Automatic CPU, RAM, GPU, storage scanning
- 💰 **Flexible Pricing** - Auto-calculation with manual override options
- 📄 **Professional PDFs** - Branded reports with FreeGeek logo

## 🚀 Quick Start (Portable Mode)

### Windows
Simply **double-click** `run.bat` - that's it!

### Linux (Debian/Ubuntu)
```bash
chmod +x run_linux.sh   # First time only
./run_linux.sh
```

### macOS
```bash
chmod +x run_macos.sh   # First time only
./run_macos.sh
```

The application starts immediately at `http://localhost:5000` - **no Python installation or setup required!**

## 📦 USB Drive Deployment

This application is designed to run from a USB drive on fresh installs:

1. **Copy the entire folder** to your USB drive
2. **Plug into any computer** (no admin rights needed)
3. **Run the script** for that platform
4. **Done!** The app launches with all dependencies included

### Requirements for Fresh Systems
- **Windows**: Works out of the box on Windows 7+ (most systems have Python pre-installed, but if not, the venv is self-contained)
- **Linux**: Requires Python 3.7+ (usually pre-installed on most distros)
- **macOS**: Requires Python 3.7+ (built-in on macOS 10.12+)

> **Note**: The venv folder contains all Python dependencies, so no internet connection or additional packages are needed!

## 📂 What's Included

```
BuildSheetGen/
├── venv/                  # Pre-configured virtual environment
│   ├── Scripts/ (Win)      # or bin/ (Linux/Mac)
│   ├── Lib/               # All Python packages included
│   └── ...
├── app.py                 # Flask web server
├── scanner.py             # Hardware detection
├── pricing.py             # Price calculation
├── report.py              # PDF generation
├── cpus.db                # CPU benchmark database (800K+ entries)
├── logo.png               # FreeGeek logo
├── requirements.txt       # Dependency list (reference only)
├── run.bat                # Windows launcher ⭐
├── run_linux.sh           # Linux launcher ⭐
├── run_macos.sh           # macOS launcher ⭐
├── templates/             # Web interface HTML
└── static/                # CSS and JavaScript
```

## 💻 Features in Detail

### Automated Hardware Detection
- CPU model, cores, and threads
- RAM capacity and type (DDR3/DDR4/DDR5)
- Storage devices with capacity and type detection
- GPU detection (integrated vs dedicated)
- Operating system identification
- Laptop vs Desktop detection

### Editable Pricing System
- **Auto-Calculation**: Prices calculated from CPU database
- **Manual Override**: Edit any component price
- **Component Prices**: CPU, RAM, Storage, GPU all editable
- **Live Updates**: Total recalculates as you type
- **Discounts**: Percentage-based discounts with live preview

### Smart Storage Management
- **Toggle Visibility**: Checkbox to show/hide each drive
- **Type Selection**: Choose HDD, SSD, or NVMe for each drive
- **Auto-Detection**: Attempts to identify drive types automatically

### Professional PDF Reports
- ✅ FreeGeek logo branding
- ✅ Clean, table-based layout
- ✅ Laptop-specific fields (screen size, battery info)
- ✅ Feature checklist (WiFi, Bluetooth, Touchscreen, Webcam)
- ✅ Simplified pricing display
- ✅ Custom builder name and notes
- ✅ Automatic opening after generation

## 🛠️ Troubleshooting

### Script won't run (Linux/macOS)
Make it executable:
```bash
chmod +x run_linux.sh  # or run_macos.sh
```

### "Python not found" error
The venv should be self-contained, but if this happens:
- **Windows**: The system may be blocking execution - right-click → "Run as Administrator"
- **Linux/macOS**: Ensure Python 3.7+ is installed (`python3 --version`)

### Port 5000 already in use
Edit `app.py` and change the port:
```python
app.run(debug=True, port=5001)  # Use different port
```

### Venv folder missing
If the venv folder is missing or corrupted, you'll need to recreate it:
```bash
# Create venv
python -m venv venv

# Install dependencies
# Windows:
venv\Scripts\pip install -r requirements.txt

# Linux/macOS:
./venv/bin/pip install -r requirements.txt
```

## 📝 Usage Guide

1. **Launch** the application using the appropriate script
2. **Wait** for the automatic hardware scan
3. **Review** detected specifications
4. **Edit** as needed:
   - RAM amount and type
   - GPU price
   - Storage drive visibility and types
   - Component prices (manual override)
5. **Add custom info**:
   - Builder name
   - Discount percentage
   - Notes
   - Laptop fields (if applicable)
6. **Select features**: WiFi, Bluetooth, Touchscreen, Webcam
7. **Generate PDF** - Click and the report opens automatically!

## 🔒 Offline Operation

This application works **completely offline**:
- All dependencies are bundled in the venv
- CPU database is local (cpus.db)
- No internet connection required
- Perfect for use in workshop environments

## 📊 Database

The included `cpus.db` contains:
- **800,000+** CPU benchmark entries
- Performance scores
- Core/thread counts
- Year-based depreciation data

## 🤝 Support

For issues or questions, contact your FreeGeek IT administrator.

## 📄 License

MIT License - Free to use and modify

---

**Built with ❤️ for FreeGeek**  
*Portable. Powerful. Professional.*
"# BuildSheetGenerator" 
