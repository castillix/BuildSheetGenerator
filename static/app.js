// Global variables
let currentSpecs = null;
let currentPricing = null;
let cpuCandidates = [];
let softwareList = ["VLC Media Player", "Google Chrome", "Mozilla Firefox", "LibreOffice"];
let cpuMode = 'auto'; // 'auto' or 'custom'

// Scan hardware
async function scanHardware() {
    try {
        showLoading(true);

        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            currentSpecs = data.specs;
            currentPricing = data.pricing;
            cpuCandidates = data.cpu_candidates || [];
            populateForm();
            // Force a recalculation to ensure backend pricing matches frontend defaults (e.g. SSD selection)
            recalculatePrice();
            updateFieldVisibility();
            showLoading(false);
        } else {
            alert('Error scanning hardware: ' + data.error);
            showLoading(false);
        }
    } catch (error) {
        alert('Error scanning hardware: ' + error.message);
        showLoading(false);
    }
}

// Populate form with scanned data
function populateForm() {
    if (!currentSpecs) return;

    // CPU Info
    const cpuSelect = document.getElementById('cpu_model_select');
    cpuSelect.innerHTML = '';

    // Populate dropdown
    if (cpuCandidates && cpuCandidates.length > 0) {
        cpuCandidates.forEach((cpu, index) => {
            const option = document.createElement('option');
            option.value = cpu.name;
            option.text = `${cpu.name} (Passmark: ${cpu.passmark})`;
            // Select the one that matches our current spec model name if exists, else first one
            if (currentSpecs.cpu_model_name && cpu.name === currentSpecs.cpu_model_name) {
                option.selected = true;
            } else if (!currentSpecs.cpu_model_name && index === 0) {
                option.selected = true;
            }
            cpuSelect.appendChild(option);
        });
    } else {
        const option = document.createElement('option');
        option.text = "No exact matches found";
        cpuSelect.appendChild(option);
    }

    document.getElementById('detected_cpu_name').textContent = currentSpecs.cpu_name || 'Unknown';
    document.getElementById('cpu_cores').value = `${currentSpecs.cpu_cores || '?'} / ${currentSpecs.cpu_threads || '?'}`;

    // RAM Info
    document.getElementById('ram_gb').value = currentSpecs.ram_gb || 0;

    // Set RAM type
    const ramType = currentSpecs.ram_type || 'DDR4';
    if (ramType.includes('DDR3')) {
        document.getElementById('ram_type').value = 'DDR3';
    } else if (ramType.includes('DDR4')) {
        document.getElementById('ram_type').value = 'DDR4';
    } else if (ramType.includes('DDR5')) {
        document.getElementById('ram_type').value = 'DDR5';
    }

    // GPU Info - populate dropdown and name field
    const gpuSelect = document.getElementById('gpu_model_select');
    gpuSelect.innerHTML = '';

    const gpuList = currentSpecs.gpu_list || [];
    if (gpuList.length > 0) {
        gpuList.forEach(gpu => {
            const option = document.createElement('option');
            option.value = gpu;
            option.text = gpu;
            gpuSelect.appendChild(option);
        });

        // Find first non-integrated GPU to select by default if possible
        let defaultGpu = gpuList[0];
        const dedicatedGpu = gpuList.find(gpu => {
            const lowGpu = gpu.toLowerCase();
            return !lowGpu.includes('intel') ||
                (!lowGpu.includes('hd graphics') && !lowGpu.includes('uhd graphics') && !lowGpu.includes('iris'));
        });

        if (dedicatedGpu) {
            defaultGpu = dedicatedGpu;
            gpuSelect.value = dedicatedGpu;
        }

        document.getElementById('gpu_name').value = defaultGpu;

        // Auto-check "Include GPU" if it looks like a dedicated one
        const isIntegrated = defaultGpu.toLowerCase().includes('intel') &&
            (defaultGpu.toLowerCase().includes('hd graphics') ||
                defaultGpu.toLowerCase().includes('uhd graphics') ||
                defaultGpu.toLowerCase().includes('iris'));

        document.getElementById('include_gpu').checked = !isIntegrated;
    } else {
        const option = document.createElement('option');
        option.text = "No GPU detected";
        gpuSelect.appendChild(option);
        document.getElementById('gpu_name').value = 'Unknown';
        document.getElementById('include_gpu').checked = false;
    }

    document.getElementById('gpu_price').value = currentSpecs.gpu_price || 0;

    // OS Info
    document.getElementById('os_name').value = currentSpecs.os_name || 'Unknown';

    // Device Type
    document.getElementById('device_type').value = currentSpecs.is_laptop ? 'Laptop' : 'Desktop';

    // Storage Devices - Create editable controls
    const storageList = document.getElementById('storage_list');
    storageList.innerHTML = '';

    if (currentSpecs.drives && currentSpecs.drives.length > 0) {
        currentSpecs.drives.forEach((drive, index) => {
            // Round capacity for display/editing
            const roundedCap = Math.round(drive.capacity_gb);

            const div = document.createElement('div');
            div.className = 'storage-drive';
            div.innerHTML = `
                <input type="checkbox" class="storage-drive-checkbox" id="drive_${index}" checked onchange="recalculatePrice()">
                <div class="storage-drive-info" style="flex-grow: 1;">
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 5px;">
                         <strong>${drive.device}</strong>
                         <select class="storage-drive-type" id="drive_type_${index}" onchange="recalculatePrice()" style="padding: 2px;">
                            <option value="HDD" ${drive.type.toLowerCase().includes('hdd') ? 'selected' : ''}>HDD</option>
                            <option value="SSD" ${drive.type.toLowerCase().includes('ssd') ? 'selected' : ''}>SSD</option>
                            <option value="NVMe" ${drive.type.toLowerCase().includes('nvme') ? 'selected' : ''}>NVMe</option>
                        </select>
                    </div>
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <input type="number" id="drive_size_${index}" value="${roundedCap}" style="width: 80px;" onchange="recalculatePrice()"> GB
                        <small> (Mounted at: ${drive.mountpoint})</small>
                    </div>
                </div>
            `;
            storageList.appendChild(div);
        });
    } else {
        storageList.innerHTML = '<p>No storage devices detected</p>';
    }

    // Render Software List
    renderSoftwareList();

    // Auto-detect features
    // WiFi - most modern systems have WiFi
    document.getElementById('feature_wifi').checked = true;

    // Bluetooth - common on laptops, less on desktops
    document.getElementById('feature_bluetooth').checked = currentSpecs.is_laptop;

    // Webcam - common on laptops
    document.getElementById('feature_webcam').checked = currentSpecs.is_laptop;

    // Sound and Microphone - common on laptops
    document.getElementById('feature_sound').checked = currentSpecs.is_laptop;
    document.getElementById('feature_microphone').checked = currentSpecs.is_laptop;

    // Serial Number
    if (currentSpecs.serial_number && currentSpecs.serial_number !== 'Unknown') {
        document.getElementById('serial_number').value = currentSpecs.serial_number;
    }
}

// Search CPU
async function searchCpu() {
    const input = document.getElementById('cpu_search_input');
    const query = input.value.trim();
    if (!query) return;

    // Change button icon to loading
    const startIcon = "🔍";
    // Find the button next to the input
    const btn = input.nextElementSibling;
    if (btn) btn.textContent = "⏳";

    try {
        const response = await fetch('/api/search-cpu', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();

        if (data.success && data.candidates) {
            cpuCandidates = data.candidates;

            // Repopulate dropdown
            const cpuSelect = document.getElementById('cpu_model_select');
            cpuSelect.innerHTML = '';

            if (cpuCandidates.length > 0) {
                cpuCandidates.forEach((cpu, index) => {
                    const option = document.createElement('option');
                    option.value = cpu.name;
                    option.text = `${cpu.name} (Passmark: ${cpu.passmark})`;
                    if (index === 0) option.selected = true;
                    cpuSelect.appendChild(option);
                });
                // Recalculate with best match
                onCpuSelectChange();
            } else {
                const option = document.createElement('option');
                option.text = "No matches found";
                cpuSelect.appendChild(option);
            }
        }
    } catch (e) {
        console.error("Search error", e);
        alert("Search failed: " + e);
    } finally {
        if (btn) btn.textContent = startIcon;
    }
}


// Update field visibility based on device type
function updateFieldVisibility() {
    if (!currentSpecs) return;

    const isLaptop = currentSpecs.is_laptop;
    const laptopFields = document.querySelectorAll('.laptop-only');

    laptopFields.forEach(field => {
        field.style.display = isLaptop ? 'block' : 'none';
    });
}

// Update pricing display
function updatePricingDisplay() {
    if (!currentPricing) return;

    const breakdown = currentPricing.breakdown;

    // Check for manual price overrides
    const cpuOverride = parseFloat(document.getElementById('cpu_price_override').value);
    const ramOverride = parseFloat(document.getElementById('ram_price_override').value);
    const storageOverride = parseFloat(document.getElementById('storage_price_override').value);

    // Display prices (use override if provided, otherwise use auto-calculated)
    const cpuPrice = !isNaN(cpuOverride) ? cpuOverride : breakdown.cpu_price;
    const ramPrice = !isNaN(ramOverride) ? ramOverride : breakdown.ram_price;
    const storagePrice = !isNaN(storageOverride) ? storageOverride : breakdown.drive_price;

    document.getElementById('cpu_price_display').textContent = `$${Math.round(cpuPrice).toFixed(0)}`;
    document.getElementById('ram_price_display').textContent = `$${Math.round(ramPrice).toFixed(0)}`;
    document.getElementById('storage_price_display').textContent = `$${Math.round(storagePrice).toFixed(0)}`;
    document.getElementById('os_modifier_display').textContent = `$${Math.round(breakdown.os_modifier).toFixed(0)}`;

    // GPU price row visibility
    const gpuPrice = parseFloat(document.getElementById('gpu_price').value) || 0;
    const includeGpu = document.getElementById('include_gpu').checked;

    if (includeGpu) {
        document.getElementById('gpu_price_row').style.display = 'flex';
        document.getElementById('gpu_price_display').textContent = `$${Math.round(gpuPrice).toFixed(0)}`;
    } else {
        document.getElementById('gpu_price_row').style.display = 'none';
    }

    // Calculate total with overrides
    const basePrice = breakdown.base_fee || 40; // Base fee from config
    const totalBeforeDiscount = basePrice + cpuPrice + ramPrice + storagePrice + gpuPrice + breakdown.os_modifier;

    // Calculate discount if applicable
    const discountPercent = parseFloat(document.getElementById('discount_percent').value) || 0;
    let finalPrice = totalBeforeDiscount;

    if (discountPercent > 0) {
        const discountAmount = totalBeforeDiscount * (discountPercent / 100);
        finalPrice -= discountAmount;

        document.getElementById('discount_row').style.display = 'flex';
        document.getElementById('discount_display').textContent = `-$${discountAmount.toFixed(0)}`;
    } else {
        document.getElementById('discount_row').style.display = 'none';
    }

    // Update total
    document.getElementById('total_price_display').textContent = `$${Math.round(finalPrice).toFixed(0)}`;
}

// Handler for GPU dropdown change
function onGpuSelectChange() {
    const gpuSelect = document.getElementById('gpu_model_select');
    const gpuNameInput = document.getElementById('gpu_name');
    gpuNameInput.value = gpuSelect.value;
    updatePricing();
}

// Update pricing when user changes values
async function updatePricing() {
    if (!currentSpecs) return;

    // Update specs with current form values
    currentSpecs.ram_gb = parseFloat(document.getElementById('ram_gb').value) || 0;
    currentSpecs.ram_type = document.getElementById('ram_type').value;
    currentSpecs.gpu_price = parseFloat(document.getElementById('gpu_price').value) || 0;
    currentSpecs.include_gpu = document.getElementById('include_gpu').checked;

    try {
        updatePricingDisplay();
    } catch (error) {
        console.error('Error updating pricing:', error);
    }
}

// Recalculate price when CPU changes
async function recalculatePrice() {
    if (!currentSpecs) return;

    const cpuSelect = document.getElementById('cpu_model_select');
    const selectedCpuName = cpuSelect.value;

    // Get Manual Passmark
    const manualPassmarkInput = document.getElementById('manual_passmark_input');
    const manualPassmark = manualPassmarkInput.value ? parseFloat(manualPassmarkInput.value) : null;

    // Update local specs
    currentSpecs.cpu_model_name = selectedCpuName;

    // We need to send current form state because other things might have changed (RAM, GPU price)
    // Actually, let's just send the specs object updated with current form values
    currentSpecs.ram_gb = parseFloat(document.getElementById('ram_gb').value) || 0;
    currentSpecs.ram_type = document.getElementById('ram_type').value;
    currentSpecs.gpu_price = parseFloat(document.getElementById('gpu_price').value) || 0;

    // Update storage drives from DOM and filter out unchecked ones
    if (currentSpecs.drives) {
        const activeDrives = [];
        currentSpecs.drives.forEach((drive, index) => {
            const checkbox = document.getElementById(`drive_${index}`);
            if (checkbox && checkbox.checked) {
                const typeSelect = document.getElementById(`drive_type_${index}`);
                if (typeSelect) {
                    drive.type = typeSelect.value;
                }
                activeDrives.push(drive);
            }
        });
        // We only send active drives for recalculation, but we don't want to permanently delete them from currentSpecs
        // so that unchecking/checking works. The backend will receive 'specs' with only active drives.
        // We need to create a copy of specs for the request.
    }

    // Create payload copy
    const specsPayload = { ...currentSpecs };

    // Pass manual passmark in logic via API call
    const payload = {
        specs: specsPayload,
        manual_passmark: manualPassmark
    };

    // Update storage drives from DOM
    if (currentSpecs.drives) {
        const activeDrives = [];
        currentSpecs.drives.forEach((drive, index) => {
            const checkbox = document.getElementById(`drive_${index}`);
            if (checkbox && checkbox.checked) {
                const typeSelect = document.getElementById(`drive_type_${index}`);
                const sizeInput = document.getElementById(`drive_size_${index}`);

                const newDrive = { ...drive };
                if (typeSelect) newDrive.type = typeSelect.value;
                if (sizeInput) newDrive.capacity_gb = parseFloat(sizeInput.value) || 0;

                activeDrives.push(newDrive);
            }
        });
        specsPayload.drives = activeDrives;
    }

    try {
        const response = await fetch('/api/recalculate-price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            currentPricing = data.pricing;
            updatePricingDisplay();

            // Update displayed specs based on the new CPU
            const used = data.pricing.specs_used;
            if (used) {
                document.getElementById('cpu_cores').value = `${used.cores} / ${used.threads}`;
                // Update currentSpecs with these new values from DB so PDF is correct
                currentSpecs.cpu_cores = used.cores;
                currentSpecs.cpu_threads = used.threads;
                // Add specific year/passmark to currentSpecs if needed by PDF
            }
        } else {
            alert('Error recalculating price: ' + data.error);
        }
    } catch (e) {
        console.error('Error:', e);
    }
}

// Rescan hardware
function rescanHardware() {
    if (confirm('This will rescan your hardware and reset all custom values. Continue?')) {
        scanHardware();
    }
}

// Generate PDF
async function generatePDF() {
    if (!currentSpecs) {
        alert('Please scan hardware first');
        return;
    }

    try {
        // Gather all form data
        const data = {
            specs: {
                ...currentSpecs,
                // Ensure we capture current form values that might differ from initial scan
                cpu_model_name: document.getElementById('cpu_model_select').value,
                os_name: document.getElementById('os_name').value,
                ram_gb: parseFloat(document.getElementById('ram_gb').value) || 0,
                ram_type: document.getElementById('ram_type').value
            },
            gpu_price: parseFloat(document.getElementById('gpu_price').value) || 0,
            computer_model: document.getElementById('computer_model').value,
            serial_number: document.getElementById('serial_number').value,
            builder_name: document.getElementById('builder_name').value,
            notes: document.getElementById('notes').value,
            discount_percent: parseFloat(document.getElementById('discount_percent').value) || 0
        };

        // Add GPU info
        data.gpu_name = document.getElementById('gpu_name').value;
        data.include_gpu = document.getElementById('include_gpu').checked;

        // Manual passmark
        const manualPassmarkInput = document.getElementById('manual_passmark_input');
        if (manualPassmarkInput && manualPassmarkInput.value) {
            data.manual_passmark = parseFloat(manualPassmarkInput.value);
        }

        // Add laptop-specific fields
        if (currentSpecs.is_laptop) {
            data.screen_size = document.getElementById('screen_size').value;
            data.battery_health = document.getElementById('battery_health').value;
            data.battery_duration = document.getElementById('battery_duration').value;
        }

        // Add custom pricing overrides
        data.price_overrides = {};
        const cpuOverride = parseFloat(document.getElementById('cpu_price_override').value);
        const ramOverride = parseFloat(document.getElementById('ram_price_override').value);
        const storageOverride = parseFloat(document.getElementById('storage_price_override').value);

        if (!isNaN(cpuOverride)) data.price_overrides.cpu_price = cpuOverride;
        if (!isNaN(ramOverride)) data.price_overrides.ram_price = ramOverride;
        if (!isNaN(storageOverride)) data.price_overrides.drive_price = storageOverride;

        // Final Price Override
        const totalOverride = parseFloat(document.getElementById('total_price_override').value);
        if (!isNaN(totalOverride)) {
            data.price_overrides.final_price = totalOverride;
        }

        // Filter storage drives and update types/sizes
        const filteredDrives = [];
        currentSpecs.drives.forEach((drive, index) => {
            const checkbox = document.getElementById(`drive_${index}`);
            if (checkbox && checkbox.checked) {
                const typeSelect = document.getElementById(`drive_type_${index}`);
                const sizeInput = document.getElementById(`drive_size_${index}`);

                filteredDrives.push({
                    ...drive,
                    type: typeSelect ? typeSelect.value : drive.type,
                    capacity_gb: sizeInput ? (parseFloat(sizeInput.value) || 0) : drive.capacity_gb
                });
            }
        });
        data.specs.drives = filteredDrives;

        // Custom CPU Handling
        if (cpuMode === 'custom') {
            data.custom_cpu = {
                name: document.getElementById('custom_cpu_name').value,
                cores: document.getElementById('custom_cpu_cores').value,
                threads: document.getElementById('custom_cpu_threads').value,
                speed: document.getElementById('custom_cpu_speed').value
            };
            // Override specs with custom values for the PDF
            data.specs.cpu_name = data.custom_cpu.name;
            data.specs.cpu_cores = data.custom_cpu.cores;
            data.specs.cpu_threads = data.custom_cpu.threads;
            // Speed isn't directly in standard specs dict but we can put it in custom fields or handle in backend
        }

        // Software List
        data.software_list = softwareList;

        // Add feature checkboxes
        data.features = {
            wifi: document.getElementById('feature_wifi').checked,
            bluetooth: document.getElementById('feature_bluetooth').checked,
            sound: document.getElementById('feature_sound').checked,
            microphone: document.getElementById('feature_microphone').checked,
            touchscreen: document.getElementById('feature_touchscreen').checked,
            webcam: document.getElementById('feature_webcam').checked
        };

        // Show loading state
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '⏳ Generating PDF...';
        button.disabled = true;

        const response = await fetch('/api/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            alert('PDF generated successfully! The file should open automatically.');
        } else {
            alert('Error generating PDF: ' + result.error);
        }

        // Restore button
        button.textContent = originalText;
        button.disabled = false;

    } catch (error) {
        alert('Error generating PDF: ' + error.message);
        // Restore button
        event.target.textContent = '📄 Generate PDF Report';
        event.target.disabled = false;
    }
}

// Show/hide loading
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
    document.getElementById('content').style.display = show ? 'none' : 'block';
}

// Handler for CPU dropdown change (Manual Mode)
function onCpuSelectChange() {
    const cpuSelect = document.getElementById('cpu_model_select');
    const selectedName = cpuSelect.value;

    // Find candidate data from our global list
    // Note: cpuCandidates is populated by scan or search
    const candidate = cpuCandidates.find(c => c.name === selectedName);

    if (candidate) {
        // Auto-fill custom fields
        document.getElementById('custom_cpu_name').value = candidate.name;
        document.getElementById('custom_cpu_cores').value = candidate.cores || '';
        document.getElementById('custom_cpu_threads').value = candidate.threads || '';
        // Use Turbo speed if available, otherwise clock.
        // DB stores these in GHz already (e.g. 3.7 or 4.7)
        const speedVal = candidate.turbo || candidate.clock;
        document.getElementById('custom_cpu_speed').value = speedVal ? Number(speedVal).toFixed(1) : '';

        // Auto-fill manual passmark
        if (candidate.passmark) {
            document.getElementById('manual_passmark_input').value = candidate.passmark;
        }
    }

    // Recalculate price
    recalculatePrice();
}

function toggleCpuMode() {
    const radios = document.getElementsByName('cpu_mode');
    for (const radio of radios) {
        if (radio.checked) {
            cpuMode = radio.value;
            break;
        }
    }

    if (cpuMode === 'custom') {
        document.getElementById('cpu_auto_section').style.display = 'none';
        document.getElementById('cpu_custom_section').style.display = 'block';
        document.getElementById('cpu_cores').disabled = true; // Not used in custom mode really

        // If switching to custom and name is empty, try to populate from current selection
        if (!document.getElementById('custom_cpu_name').value) {
            onCpuSelectChange();
        }
    } else {
        document.getElementById('cpu_auto_section').style.display = 'block';
        document.getElementById('cpu_custom_section').style.display = 'none';
        document.getElementById('cpu_cores').disabled = false;
    }
}

// Software List Functions
function renderSoftwareList() {
    const container = document.getElementById('software_list_container');
    container.innerHTML = '';

    softwareList.forEach((sw, index) => {
        const chip = document.createElement('div');
        chip.style.backgroundColor = '#e8f8f5';
        chip.style.border = '1px solid #2ecc71';
        chip.style.borderRadius = '20px';
        chip.style.padding = '5px 12px';
        chip.style.display = 'flex';
        chip.style.alignItems = 'center';
        chip.style.gap = '8px';

        chip.innerHTML = `
            <span>${sw}</span>
            <span onclick="removeSoftwareItem(${index})" style="cursor: pointer; color: #e74c3c; font-weight: bold;">&times;</span>
        `;
        container.appendChild(chip);
    });
}

function addSoftwareItem() {
    const input = document.getElementById('new_software_input');
    const val = input.value.trim();
    if (val) {
        softwareList.push(val);
        input.value = '';
        renderSoftwareList();
    }
}

function removeSoftwareItem(index) {
    softwareList.splice(index, 1);
    renderSoftwareList();
}
