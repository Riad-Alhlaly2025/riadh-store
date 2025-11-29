// Custom Admin JavaScript for Enhanced Interface

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize charts
    initCharts();
    
    // Initialize filters
    initFilters();
    
    // Initialize export functionality
    initExport();
    
    // Initialize quick actions
    initQuickActions();
});

// Initialize tooltips
function initTooltips() {
    // Add tooltip functionality to elements with data-tooltip attribute
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            if (tooltipText) {
                // Create tooltip element
                const tooltip = document.createElement('div');
                tooltip.className = 'admin-tooltip';
                tooltip.textContent = tooltipText;
                document.body.appendChild(tooltip);
                
                // Position tooltip
                const rect = this.getBoundingClientRect();
                tooltip.style.position = 'absolute';
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
                tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            }
        });
        
        element.addEventListener('mouseleave', function() {
            // Remove tooltip
            const tooltips = document.querySelectorAll('.admin-tooltip');
            tooltips.forEach(tooltip => tooltip.remove());
        });
    });
}

// Initialize charts
function initCharts() {
    // This function is called after specific chart data is loaded
    // Individual chart initialization happens in template-specific scripts
}

// Initialize filters
function initFilters() {
    // Toggle advanced filters
    const filterToggles = document.querySelectorAll('.filter-toggle');
    filterToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const filterContent = this.closest('.advanced-filters').querySelector('.filter-content');
            if (filterContent.style.display === 'none' || !filterContent.style.display) {
                filterContent.style.display = 'grid';
                this.textContent = 'إخفاء الفلاتر المتقدمة';
            } else {
                filterContent.style.display = 'none';
                this.textContent = 'عرض الفلاتر المتقدمة';
            }
        });
    });
    
    // Reset filters
    const resetButtons = document.querySelectorAll('.btn-reset');
    resetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form) {
                form.reset();
            }
        });
    });
}

// Initialize export functionality
function initExport() {
    // Export buttons functionality
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const format = this.getAttribute('data-format');
            exportReport(format);
        });
    });
}

// Export report function
function exportReport(format) {
    // Show loading indicator
    showLoadingIndicator();
    
    // Simulate export process
    setTimeout(() => {
        hideLoadingIndicator();
        showMessage(`تم تصدير التقرير بتنسيق ${format.toUpperCase()} بنجاح!`, 'success');
    }, 1500);
}

// Initialize quick actions
function initQuickActions() {
    // Add click handlers to action cards
    const actionCards = document.querySelectorAll('.action-card');
    actionCards.forEach(card => {
        card.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            if (action) {
                executeAction(action);
            }
        });
    });
}

// Execute quick action
function executeAction(action) {
    switch(action) {
        case 'refresh':
            location.reload();
            break;
        case 'export':
            exportReport('pdf');
            break;
        default:
            showMessage('تم تنفيذ الإجراء بنجاح!', 'success');
    }
}

// Show loading indicator
function showLoadingIndicator() {
    // Create loading overlay
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>جاري التحميل...</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Hide loading indicator
function hideLoadingIndicator() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Show message
function showMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `admin-message ${type}`;
    messageEl.textContent = message;
    
    // Add to body
    document.body.appendChild(messageEl);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

// Format currency
function formatCurrency(amount, currency = 'ر.س') {
    return parseFloat(amount).toLocaleString('ar-SA') + ' ' + currency;
}

// Format number
function formatNumber(number) {
    return parseFloat(number).toLocaleString('ar-SA');
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA');
}

// Format datetime
function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleDateString('ar-SA') + ' ' + date.toLocaleTimeString('ar-SA');
}

// Add event listener for dynamic content
document.addEventListener('admin-content-loaded', function() {
    initTooltips();
    initCharts();
});

// Utility function to get CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// AJAX helper function
async function adminAjax(url, options = {}) {
    const defaultOptions = {
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    };
    
    const finalOptions = Object.assign({}, defaultOptions, options);
    
    try {
        const response = await fetch(url, finalOptions);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('AJAX request failed:', error);
        showMessage('حدث خطأ أثناء معالجة الطلب', 'error');
        throw error;
    }
}

// Chart helper functions
function createLineChart(ctx, data, options = {}) {
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: Object.assign({
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }, options)
    });
}

function createBarChart(ctx, data, options = {}) {
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: Object.assign({
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }, options)
    });
}

function createPieChart(ctx, data, options = {}) {
    return new Chart(ctx, {
        type: 'pie',
        data: data,
        options: Object.assign({
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }, options)
    });
}

function createDoughnutChart(ctx, data, options = {}) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: Object.assign({
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }, options)
    });
}