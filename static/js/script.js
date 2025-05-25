// Emergency Response App - Main JavaScript File

// Global variables
let userLocation = null;
let emergencyAlerts = [];
let notificationPermission = false;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// App initialization
function initializeApp() {
    console.log('Emergency Response App initialized');

    // Request notification permission
    requestNotificationPermission();

    // Initialize location services
    initializeLocation();

    // Set up periodic checks for emergency alerts
    setInterval(checkForEmergencyAlerts, 30000); // Check every 30 seconds

    // Initialize service worker for offline functionality
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    }
}

// Notification functions
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
            notificationPermission = permission === 'granted';
            console.log('Notification permission:', permission);
        });
    }
}

function showNotification(title, body, icon = '/static/images/emergency-icon.png') {
    if (notificationPermission) {
        new Notification(title, {
            body: body,
            icon: icon,
            badge: icon,
            vibrate: [200, 100, 200],
            requireInteraction: true
        });
    }
}

// Location functions
function initializeLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
                console.log('User location obtained:', userLocation);
            },
            function(error) {
                console.warn('Location error:', error.message);
                handleLocationError(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            }
        );
    }
}

function handleLocationError(error) {
    let message = 'Location access denied. ';
    switch(error.code) {
        case error.PERMISSION_DENIED:
            message += 'Please enable location services for emergency alerts.';
            break;
        case error.POSITION_UNAVAILABLE:
            message += 'Location information unavailable.';
            break;
        case error.TIMEOUT:
            message += 'Location request timed out.';
            break;
    }
    console.warn(message);
}

// Emergency alert functions
function checkForEmergencyAlerts() {
    // Simulate checking for emergency alerts
    // In a real app, this would make an API call to check for new alerts

    if (Math.random() < 0.01) { // 1% chance of simulated alert
        const alertTypes = [
            {
                type: 'fire',
                title: 'Fire Alert',
                message: 'Fire reported in your area. Stay alert and follow evacuation instructions if necessary.',
                severity: 'high'
            },
            {
                type: 'weather',
                title: 'Weather Alert',
                message: 'High wind warning. Increased fire risk in your area.',
                severity: 'medium'
            }
        ];

        const alert = alertTypes[Math.floor(Math.random() * alertTypes.length)];
        showEmergencyAlert(alert);
    }
}

function showEmergencyAlert(alert) {
    // Show browser notification
    showNotification(alert.title, alert.message);

    // Add to alerts array
    emergencyAlerts.unshift({
        ...alert,
        timestamp: new Date(),
        id: Date.now()
    });

    // Show in-app alert
    showInAppAlert(alert);
}

function showInAppAlert(alert) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${alert.severity === 'high' ? 'danger' : 'warning'} alert-dismissible fade show position-fixed`;
    alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';

    alertContainer.innerHTML = `
        <strong>${alert.title}</strong><br>
        ${alert.message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertContainer);

    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 10000);
}

// Emergency reporting functions
function reportEmergency(emergencyData) {
    // Add location if available
    if (userLocation) {
        emergencyData.location = userLocation;
    }

    // Add timestamp
    emergencyData.timestamp = new Date().toISOString();

    // Show loading state
    showLoadingState('Reporting emergency...');

    // Simulate API call
    setTimeout(() => {
        hideLoadingState();
        showNotification('Emergency Reported', 'Your emergency report has been submitted successfully.');

        // In a real app, this would send data to emergency services
        console.log('Emergency reported:', emergencyData);

        // Show confirmation
        showSuccessMessage('Emergency reported successfully! Emergency services have been notified.');
    }, 2000);
}

// UI helper functions
function showLoadingState(message = 'Loading...') {
    const loader = document.createElement('div');
    loader.id = 'globalLoader';
    loader.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    loader.style.cssText = 'background: rgba(0,0,0,0.7); z-index: 10000;';

    loader.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner-border mb-3" role="status"></div>
            <div>${message}</div>
        </div>
    `;

    document.body.appendChild(loader);
}

function hideLoadingState() {
    const loader = document.getElementById('globalLoader');
    if (loader) {
        loader.remove();
    }
}

function showSuccessMessage(message) {
    const toast = document.createElement('div');
    toast.className = 'toast position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '10001';

    toast.innerHTML = `
        <div class="toast-header bg-success text-white">
            <i class="fas fa-check-circle me-2"></i>
            <strong class="me-auto">Success</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    document.body.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function showErrorMessage(message) {
    const toast = document.createElement('div');
    toast.className = 'toast position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '10001';

    toast.innerHTML = `
        <div class="toast-header bg-danger text-white">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong class="me-auto">Error</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    document.body.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Utility functions
function formatDistance(meters) {
    if (meters < 1000) {
        return Math.round(meters) + ' m';
    } else {
        return (meters / 1000).toFixed(1) + ' km';
    }
}

function formatTime(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return minutes + ' minutes ago';
    if (minutes < 1440) return Math.floor(minutes / 60) + ' hours ago';
    return Math.floor(minutes / 1440) + ' days ago';
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c * 1000; // Distance in meters
}

// Offline functionality
function isOnline() {
    return navigator.onLine;
}

function handleOffline() {
    showErrorMessage('You are currently offline. Some features may not be available.');
}

function handleOnline() {
    showSuccessMessage('Connection restored. All features are now available.');
}

// Event listeners for online/offline
window.addEventListener('online', handleOnline);
window.addEventListener('offline', handleOffline);

// Emergency contact functions
function callEmergencyServices() {
    const choice = prompt('Which emergency service do you need?\n\n1 - Fire Rescue (118)\n2 - Police (117)\n3 - Ambulance (119)\n\nEnter 1, 2, or 3:');

    switch(choice) {
        case '1':
            window.location.href = 'tel:118';
            break;
        case '2':
            window.location.href = 'tel:117';
            break;
        case '3':
            window.location.href = 'tel:119';
            break;
        default:
            alert('Emergency Services in Cameroon:\n\n🔥 Fire Rescue: 118\n👮 Police: 117\n🚑 Ambulance: 119');
    }
}

// First aid timer functions
function startFirstAidTimer(duration = 30) {
    let timeLeft = duration;
    const timerDisplay = document.createElement('div');
    timerDisplay.className = 'position-fixed top-0 start-50 translate-middle-x bg-success text-white p-3 rounded-bottom';
    timerDisplay.style.zIndex = '10000';

    const updateTimer = () => {
        timerDisplay.innerHTML = `
            <div class="text-center">
                <i class="fas fa-clock me-2"></i>
                <strong>CPR Timer: ${timeLeft}s</strong>
                <br><small>Continue compressions</small>
            </div>
        `;

        if (timeLeft <= 0) {
            timerDisplay.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Give 2 rescue breaths</strong>
                    <br><small>Then restart compressions</small>
                </div>
            `;
            setTimeout(() => {
                if (timerDisplay.parentNode) {
                    timerDisplay.remove();
                }
            }, 3000);
        } else {
            timeLeft--;
            setTimeout(updateTimer, 1000);
        }
    };

    document.body.appendChild(timerDisplay);
    updateTimer();
}

// Export functions for global use
window.EmergencyApp = {
    reportEmergency,
    showNotification,
    callEmergencyServices,
    startFirstAidTimer,
    showSuccessMessage,
    showErrorMessage,
    userLocation: () => userLocation,
    emergencyAlerts: () => emergencyAlerts
};
