from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import os

def generate_pdf(specs, price_data, custom_fields=None, filename="BuildSheet.pdf"):
    """
    Generates a PDF report with the specs and price breakdown.
    New Layout: Logo TR, Header TL, Specs List, OS Bottom.
    """
    if custom_fields is None:
        custom_fields = {}
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # --- Header Section ---
    
    # 1. Logo Analysis (Top Right)
    # Support frozen app
    import sys
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    logo_path = os.path.join(base_path, 'resources', 'logo.png')
    
    if os.path.exists(logo_path):
        # Position logo in top right corner
        # x = width - image_width - margin
        c.drawImage(logo_path, width - 180, height - 100, width=150, height=75, preserveAspectRatio=True, mask='auto', anchor='ne')

    # 2. Computer Info (Top Left)
    y = height - 50
    c.setFont("Helvetica-Bold", 24)
    # Model Name
    model_name = custom_fields.get('computer_model', 'Unknown Model')
    c.drawString(50, y, model_name)
    y -= 25
    
    c.setFont("Helvetica", 12)
    # Serial Number
    serial = custom_fields.get('serial_number', 'N/A')
    c.drawString(50, y, f"Serial: {serial}")
    y -= 15
    
    # Builder / Date
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    builder = custom_fields.get('builder_name', '')
    if builder:
        c.drawString(50, y, f"Built by: {builder} on {date_str}")
    else:
        c.drawString(50, y, f"Date: {date_str}")
        
    y -= 25
    # Separator Line
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.line(50, y, width - 50, y)
    y -= 40
    
    # --- Specs Section ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Hardware Specifications")
    y -= 30 # Increased initial gap slightly
    
    # We need to use Paragraphs for mixed formatting (Bold Label + Normal Value inline)
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontName = "Helvetica"
    normal_style.fontSize = 12
    normal_style.leading = 16
    
    # 1. CPU Section (Split into two lines)
    custom_cpu = custom_fields.get('custom_cpu')
    
    if custom_cpu:
        cpu_name = custom_cpu.get('name', 'Unknown')
        cores = custom_cpu.get('cores', '?')
        threads = custom_cpu.get('threads', '?')
        clock_str = custom_cpu.get('speed', '')
        if clock_str and not 'GHz' in str(clock_str) and not 'MHz' in str(clock_str):
             clock_str += " GHz"
    else:
        cpu_name = specs.get('cpu_name', 'Unknown')
        if '@' in cpu_name:
            cpu_name = cpu_name.split('@')[0].strip()
            
        db_specs = price_data.get('specs_used', {})
        cores = db_specs.get('cores', specs.get('cpu_cores', '?'))
        threads = db_specs.get('threads', specs.get('cpu_threads', '?'))
        
        clock_speed = db_specs.get('clock')
        if not clock_speed:
             raw_name = specs.get('cpu_name', '')
             if '@' in raw_name:
                 clock_speed = raw_name.split('@')[1].strip()
        
        clock_str = ""
        if clock_speed:
            if isinstance(clock_speed, (int, float)):
                 clock_str = f"{clock_speed/1000:.2f} GHz" if clock_speed > 100 else f"{clock_speed} GHz"
            else:
                 clock_str = str(clock_speed)
    
    # Render Line 1: Processor Name
    p1 = Paragraph(f"<b>Processor:</b> {cpu_name}", normal_style)
    p1_width, p1_height = p1.wrap(width - 100, height)
    p1.drawOn(c, 50, y - p1_height)
    y -= (p1_height + 5)
    
    # Render Line 2: Stats
    # Using &nbsp; for spacing
    cpu_line_text = f"<b>Cores:</b> {cores}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Threads:</b> {threads}"
    if clock_str:
        cpu_line_text += f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Speed:</b> {clock_str}"
        
    p2 = Paragraph(cpu_line_text, normal_style)
    p2_width, p2_height = p2.wrap(width - 100, height)
    p2.drawOn(c, 50, y - p2_height)
    
    y -= (p2_height + 25) # Gap before next section
    
    # 2. Other Specs Table
    spec_rows = []
    
    # RAM
    ram_gb = specs.get('ram_gb', 0)
    ram_type = specs.get('ram_type', 'Unknown')
    spec_rows.append(["Memory", f"{ram_gb} GB {ram_type}"])
    
    # Storage
    if specs.get('drives'):
        drive_strs = []
        for drive in specs['drives']:
            drive_strs.append(f"{drive['capacity_gb']} GB {drive.get('type', 'Drive')}")
        spec_rows.append(["Storage", "\n".join(drive_strs)])
    else:
        spec_rows.append(["Storage", "None Detected"])
        
    # GPU (Conditional)
    include_gpu = custom_fields.get('include_gpu', True)
    gpu_name = custom_fields.get('gpu_name', specs.get('gpu_name', ''))
    
    if include_gpu and gpu_name and gpu_name != 'Unknown':
        spec_rows.append(["Graphics", gpu_name])
        
    # Laptop Specifics
    if specs.get('is_laptop'):
        if custom_fields.get('screen_size'):
            size_str = str(custom_fields.get('screen_size'))
            if 'inch' not in size_str.lower() and '"' not in size_str:
                 size_str += " Inches"
            spec_rows.append(["Screen Size", size_str])
        if custom_fields.get('battery_health'):
            spec_rows.append(["Battery Health", custom_fields.get('battery_health')])
        if custom_fields.get('battery_duration'):
            spec_rows.append(["Battery Duration", f"{custom_fields.get('battery_duration')} Hours"])

    # Draw Specs Table
    # Use a clean layout, maybe bold labels
    t_style = TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (0,-1), 20),
    ])
    
    t = Table(spec_rows, colWidths=[1.5*inch, 5*inch])
    t.setStyle(t_style)
    w, h = t.wrap(width, height)
    t.drawOn(c, 50, y - h)
    y -= (h + 30)

    # --- Features Section (Checklist) ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Features & Connectivity")
    y -= 30
    
    features = custom_fields.get('features', {})
    
    c.setFont("Helvetica", 12)
    
    # List of all features to display
    all_features = [
        ('wifi', 'WiFi'),
        ('bluetooth', 'Bluetooth'),
        ('webcam', 'Webcam'),
        ('touchscreen', 'Touchscreen'),
        ('sound', 'Sound'),
        ('microphone', 'Microphone')
    ]
    
    # Display in 2 columns
    col1_x = 60
    col2_x = 250
    
    for i, (key, label) in enumerate(all_features):
        is_included = features.get(key, False)
        x_pos = col1_x if i % 2 == 0 else col2_x
        
        # Checkbox style
        box_size = 10
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        
        # Draw box
        c.rect(x_pos, y, box_size, box_size, fill=0, stroke=1)
        
        # Draw checkmark inside if included
        if is_included:
            c.setLineWidth(1.5)
            # Simple checkmark path
            p = c.beginPath()
            p.moveTo(x_pos + 2, y + 5)
            p.lineTo(x_pos + 4, y + 2)
            p.lineTo(x_pos + 8, y + 8)
            c.drawPath(p, stroke=1, fill=0)
            c.setLineWidth(1) # Reset
            
        c.setFillColor(colors.black)
        c.drawString(x_pos + 18, y + 1, label)
        
        if i % 2 != 0:
            y -= 20
            
    if len(all_features) % 2 != 0:
        y -= 20
        
    y -= 20
    
    # --- Software Included Section ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Software Included:")
    c.setFont("Helvetica", 11)
    
    software_list = custom_fields.get('software_list')
    if not software_list or len(software_list) == 0:
         software_list = ["VLC Media Player", "Google Chrome", "Mozilla Firefox", "LibreOffice"]
    # Inline layout
    sw_x_start = 180
    sw_x = sw_x_start
    line_height = 20
    
    for sw in software_list:
        # Calculate width of this item
        text_width = c.stringWidth(sw, "Helvetica", 10)
        item_total_width = text_width + 40 # 15 for checkbox/gap + text + 25 padding
        
        # Check if we need to wrap
        if sw_x + item_total_width > (width - 50):
            sw_x = sw_x_start
            y -= line_height
            
        # Checkbox (Always checked)
        c.rect(sw_x, y, 10, 10, fill=0, stroke=1)
        # Checkmark
        p = c.beginPath()
        p.moveTo(sw_x + 2, y + 5)
        p.lineTo(sw_x + 4, y + 2)
        p.lineTo(sw_x + 8, y + 8)
        c.setLineWidth(1.5)
        c.drawPath(p, stroke=1, fill=0)
        c.setLineWidth(1) # Reset
        
        c.drawString(sw_x + 15, y + 1, sw)
        
        # Advance x based on text width + padding
        sw_x += item_total_width
        
    y -= 30 # Update main y position after software line
        
    # --- OS Section (Moved above Price) ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Operating System:")
    c.setFont("Helvetica", 14)
    # scanner.py now returns comprehensive OS string, e.g. "Windows 10 Pro 22H2"
    os_text = specs.get('os_name', 'Unknown')
    c.drawString(180, y, os_text)
    
    y = y - 30 # Spacing before price
    
    # --- Price Section (Right Aligned or Separate Box?) ---
    # Let's put a price box
    
    price_y = y
    
    # Calculate Total
    final_price = price_data.get('final_price', 0)
    
    # Discount
    if price_data.get('discount_amount', 0) > 0:
        c.setFillColor(colors.red)
        c.drawString(50, price_y, f"Discount: -${price_data.get('discount_amount'):.2f}")
        c.setFillColor(colors.black)
        price_y -= 15
        
    # Final Price Box
    # Final Price Box (Left Aligned)
    box_x = 50
    box_w = 200
    
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.HexColor('#e8f8f5')) # Light green bg
    c.rect(box_x, price_y - 60, box_w, 70, fill=1, stroke=1)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(box_x + (box_w/2), price_y - 15, "TOTAL PRICE")
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor('#27ae60'))
    # Force integer formatting with .0f
    c.drawCentredString(box_x + (box_w/2), price_y - 45, f"${final_price:.0f}")
    c.setFillColor(colors.black)
    
    # Barcode Placeholder
    # Small black outline rectangle below the price box
    barcode_w = 120 # 15% narrower (was 150)
    barcode_h = 40  # 15% taller (was 40)
    barcode_x = box_x + (box_w - barcode_w) / 2
    barcode_y = price_y - 60 - 20 - barcode_h # 20px gap below price box
    
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(barcode_x, barcode_y, barcode_w, barcode_h, fill=0, stroke=1)
    
    c.setFont("Helvetica", 8)
    c.drawCentredString(barcode_x + (barcode_w/2), barcode_y + 15, "")
    
    y = barcode_y - 20 # Move down past barcode box

    # --- Notes ---
    if custom_fields.get('notes'):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Notes:")
        y -= 20
        c.setFont("Helvetica", 11)
        # Wrap notes
        text_obj = c.beginText(50, y)
        text_obj.setFont("Helvetica", 10)
        # simplistic wrapping for reportlab textobject?
        # Better to use string drawing with manual wrap or Paragraph (but requires platypus flow)
        # Using the manual wrap logic from before for safety
        max_w = width - 100
        words = custom_fields['notes'].split()
        line = []
        for word in words:
            if c.stringWidth(' '.join(line + [word]), "Helvetica", 10) < max_w:
                line.append(word)
            else:
                c.drawString(50, y, ' '.join(line))
                y -= 14
                line = [word]
        if line:
            c.drawString(50, y, ' '.join(line))
            y -= 14
        y -= 20

    c.save()
    return filename
