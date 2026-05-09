// Focus on ID input field when page loads
document.addEventListener('DOMContentLoaded', function() {
    const idField = document.getElementById('id_value');
    if (idField) {
        idField.focus();
    }
    
    // Initialize bootstrap components
    initializeBootstrapComponents();
    
    // Check URL params for modal display
    checkUrlParamsForModals();
    
    // Add event listeners for visitor modal from flash messages
    setupVisitorModalListeners();
});

// Initialize Bootstrap components like popovers, tooltips, etc.
function initializeBootstrapComponents() {
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Check URL parameters to see if we need to show modals
function checkUrlParamsForModals() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Handle supplier form display
    if (urlParams.get('show_supplier_form') === 'true') {
        const supplierId = urlParams.get('supplier_id');
        const facilityLocation = urlParams.get('facility_location');
        
        if (supplierId && facilityLocation) {
            document.getElementById('supplier_id_input').value = supplierId;
            document.getElementById('facility_location_input').value = facilityLocation;
            
            // Show the modal
            const supplierModal = new bootstrap.Modal(document.getElementById('supplierModal'));
            supplierModal.show();
        }
    }
}

// Function to open the visitor modal when needed
function showVisitorModal() {
    const visitorModal = new bootstrap.Modal(document.getElementById('visitorModal'));
    visitorModal.show();
}

// Setup listener for "Add visitor" links in flash messages
function setupVisitorModalListeners() {
    const flashMessages = document.querySelectorAll('.alert-warning');
    flashMessages.forEach(function(flash) {
        if (flash.textContent.includes('Add as visitor?')) {
            // Check if button already exists
            if (!flash.querySelector('.btn-warning')) {
                // Add a button to the flash message
                const btn = document.createElement('button');
                btn.className = 'btn btn-sm btn-warning ms-2';
                btn.textContent = 'Add Visitor';
                btn.onclick = function() {
                    showVisitorModal();
                    return false;
                };
                flash.appendChild(btn);
            }
        }
    });
}

// RFID scanning simulation for testing without hardware
// This function could be enabled during development to simulate card scans
function simulateRfidScan(rfidValue) {
    const idField = document.getElementById('id_value');
    if (idField) {
        idField.value = rfidValue;
        // Submit the form
        idField.closest('form').submit();
    }
}