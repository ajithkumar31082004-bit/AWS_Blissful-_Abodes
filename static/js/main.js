// Main JavaScript file for Blissful Abodes

// Toast notification function
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#28a745' : type === 'danger' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#2d9cdb'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Navigation Toggle for Mobile
        const navToggle = document.getElementById('navToggle');
        const navLinks = document.getElementById('navLinks');
        
        if (navToggle && navLinks) {
            navToggle.addEventListener('click', function() {
                navLinks.classList.toggle('active');
                navToggle.innerHTML = navLinks.classList.contains('active') 
                    ? '<i class="fas fa-times"></i>' 
                    : '<i class="fas fa-bars"></i>';
            });
            
            // Close nav when clicking outside on mobile
            document.addEventListener('click', function(event) {
                if (window.innerWidth <= 768) {
                    if (!navToggle.contains(event.target) && !navLinks.contains(event.target)) {
                        navLinks.classList.remove('active');
                        navToggle.innerHTML = '<i class="fas fa-bars"></i>';
                    }
                }
            });
        }
        
        // Close flash messages
        const flashCloseButtons = document.querySelectorAll('.flash-close');
        flashCloseButtons.forEach(button => {
            button.addEventListener('click', function() {
                const flash = this.closest('.flash');
                if (flash) {
                    flash.style.animation = 'slideOut 0.3s ease forwards';
                    setTimeout(() => {
                        try {
                            flash.remove();
                        } catch (e) {
                            console.log('Error removing flash:', e);
                        }
                    }, 300);
                }
            });
        });
        
        // Auto-remove flash messages after 5 seconds
        setTimeout(() => {
            const flashes = document.querySelectorAll('.flash');
            flashes.forEach(flash => {
                flash.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => {
                    try {
                        flash.remove();
                    } catch (e) {
                        console.log('Error removing flash:', e);
                    }
                }, 300);
            });
        }, 5000);
        
        // Date picker enhancements
        const checkInInputs = document.querySelectorAll('input[type="date"][name="check_in"]');
        const checkOutInputs = document.querySelectorAll('input[type="date"][name="check_out"]');
        
        // Set min date for check-in to today
        const today = new Date().toISOString().split('T')[0];
        checkInInputs.forEach(input => {
            try {
                input.min = today;
                
                // Update check-out min when check-in changes
                input.addEventListener('change', function() {
                    checkOutInputs.forEach(outInput => {
                        outInput.min = this.value;
                        if (outInput.value && outInput.value < this.value) {
                            outInput.value = this.value;
                        }
                    });
                });
            } catch (e) {
                console.log('Error setting date input:', e);
            }
        });
        
        // Form validation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                try {
                    const requiredInputs = this.querySelectorAll('[required]');
                    let isValid = true;
                    
                    requiredInputs.forEach(input => {
                        if (!input.value.trim()) {
                            input.style.borderColor = 'var(--danger)';
                            isValid = false;
                            
                            // Reset border color when user starts typing
                            input.addEventListener('input', function() {
                                this.style.borderColor = '';
                            });
                        }
                    });
                    
                    if (!isValid) {
                        event.preventDefault();
                        showToast('Please fill in all required fields', 'warning');
                    }
                } catch (e) {
                    console.log('Form validation error:', e);
                }
            });
        });
        
        // Room availability check
        const bookButtons = document.querySelectorAll('.btn-book');
        bookButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                try {
                    const isAvailable = this.getAttribute('data-available') === 'true';
                    if (!isAvailable) {
                        e.preventDefault();
                        showToast('This room is no longer available', 'warning');
                    }
                } catch (e) {
                    console.log('Error checking availability:', e);
                }
            });
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                try {
                    const href = this.getAttribute('href');
                    if (href !== '#' && href.startsWith('#')) {
                        e.preventDefault();
                        const target = document.querySelector(href);
                        if (target) {
                            target.scrollIntoView({
                                behavior: 'smooth',
                                block: 'start'
                            });
                        }
                    }
                } catch (e) {
                    console.log('Error with smooth scroll:', e);
                }
            });
        });
        
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(element => {
            element.addEventListener('mouseenter', function() {
                try {
                    const tooltip = document.createElement('div');
                    tooltip.className = 'tooltip';
                    tooltip.textContent = this.getAttribute('data-tooltip');
                    document.body.appendChild(tooltip);
                    
                    const rect = this.getBoundingClientRect();
                    tooltip.style.position = 'fixed';
                    tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
                    tooltip.style.left = (rect.left + rect.width/2 - tooltip.offsetWidth/2) + 'px';
                    
                    this._tooltip = tooltip;
                } catch (e) {
                    console.log('Error creating tooltip:', e);
                }
            });
            
            element.addEventListener('mouseleave', function() {
                try {
                    if (this._tooltip) {
                        this._tooltip.remove();
                        delete this._tooltip;
                    }
                } catch (e) {
                    console.log('Error removing tooltip:', e);
                }
            });
        });
        
        // Add CSS for tooltips
        const tooltipStyle = document.createElement('style');
        tooltipStyle.textContent = `
            .tooltip {
                position: fixed;
                background: var(--primary);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 0.85rem;
                z-index: 10000;
                pointer-events: none;
                white-space: nowrap;
                box-shadow: var(--shadow);
            }
            
            .tooltip:after {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: var(--primary) transparent transparent transparent;
            }
        `;
        document.head.appendChild(tooltipStyle);
        
        // Real-time updates for room availability
        if (window.location.pathname.includes('/rooms') || window.location.pathname.includes('/dashboard')) {
            setInterval(checkRoomAvailability, 30000); // Check every 30 seconds
        }
        
        async function checkRoomAvailability() {
            try {
                const response = await fetch('/api/rooms/available');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        updateRoomCards(data.rooms);
                    } else {
                        console.log('API error:', data.error);
                    }
                }
            } catch (error) {
                console.log('Availability check failed:', error);
            }
        }
        
        function updateRoomCards(rooms) {
            try {
                rooms.forEach(room => {
                    const roomCard = document.querySelector(`[data-room-id="${room.room_id}"]`);
                    if (roomCard) {
                        const badge = roomCard.querySelector('.availability-badge');
                        if (badge) {
                            badge.textContent = room.availability;
                            badge.className = `badge badge-${room.availability === 'available' ? 'success' : 'danger'}`;
                        }
                        
                        const bookBtn = roomCard.querySelector('.btn-book');
                        if (bookBtn) {
                            bookBtn.disabled = room.availability !== 'available';
                            bookBtn.setAttribute('data-available', room.availability === 'available');
                        }
                    }
                });
            } catch (e) {
                console.log('Error updating room cards:', e);
            }
        }
        
        // Add loading states for buttons
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function() {
                try {
                    if (this.type === 'submit' || this.getAttribute('type') === 'submit') {
                        const originalHTML = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                        this.disabled = true;
                        
                        // Reset after 5 seconds (in case form submission fails)
                        setTimeout(() => {
                            this.innerHTML = originalHTML;
                            this.disabled = false;
                        }, 5000);
                    }
                } catch (e) {
                    console.log('Error with button loading state:', e);
                }
            });
        });
        
        // Password strength indicator
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            input.addEventListener('input', function() {
                try {
                    const strengthIndicator = this.nextElementSibling;
                    if (strengthIndicator && strengthIndicator.classList.contains('password-strength')) {
                        const password = this.value;
                        let strength = 0;
                        
                        if (password.length >= 8) strength++;
                        if (/[A-Z]/.test(password)) strength++;
                        if (/[0-9]/.test(password)) strength++;
                        if (/[^A-Za-z0-9]/.test(password)) strength++;
                        
                        const strengthText = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
                        const strengthColors = ['#dc3545', '#ffc107', '#ffc107', '#28a745', '#28a745'];
                        
                        strengthIndicator.textContent = 'Password strength: ' + strengthText[strength];
                        strengthIndicator.style.color = strengthColors[strength];
                    }
                } catch (e) {
                    console.log('Error with password strength:', e);
                }
            });
        });
        
        // Add password strength indicator after password inputs
        passwordInputs.forEach(input => {
            try {
                if (input.id.includes('password') && !input.id.includes('confirm')) {
                    const indicator = document.createElement('div');
                    indicator.className = 'password-strength';
                    indicator.style.fontSize = '0.85rem';
                    indicator.style.marginTop = '5px';
                    indicator.textContent = 'Password strength: Very Weak';
                    indicator.style.color = '#dc3545';
                    
                    input.parentNode.insertBefore(indicator, input.nextSibling);
                }
            } catch (e) {
                console.log('Error adding password strength indicator:', e);
            }
        });
        
        // Initialize any charts on the page
        if (typeof Chart !== 'undefined') {
            try {
                initializeCharts();
            } catch (e) {
                console.log('Error initializing charts:', e);
            }
        }
        
    } catch (error) {
        console.error('Error in main.js initialization:', error);
        // Show error to user if critical
        showToast('Error initializing page. Please refresh.', 'danger');
    }
});

// Chart initialization function
function initializeCharts() {
    try {
        const chartCanvases = document.querySelectorAll('canvas[data-chart]');
        
        chartCanvases.forEach(canvas => {
            const ctx = canvas.getContext('2d');
            const chartType = canvas.getAttribute('data-chart-type') || 'bar';
            const chartData = JSON.parse(canvas.getAttribute('data-chart-data') || '{}');
            
            new Chart(ctx, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
    } catch (e) {
        console.log('Error in chart initialization:', e);
    }
}

// Export functions for use in other scripts
window.BlissfulAbodes = {
    showToast: window.showToast,
    initializeCharts: initializeCharts
};

// Global error handler
window.onerror = function(message, source, lineno, colno, error) {
    console.error('Global error:', { message, source, lineno, colno, error });
    return false; // Let default handler run
};

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred', 'danger');
});