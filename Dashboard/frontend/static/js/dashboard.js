// Vehicle Dashboard JavaScript
class VehicleDashboard {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.currentData = {
            speed: 0,
            rpm: 0,
            lane_warning: null,
            emergency_stop: { active: false, distance: 0 },
            pedestrian_warning: null
        };
        
        this.init();
    }

    init() {
        this.initializeElements();
        this.initializeEventListeners();
        this.startDataPolling();
        this.updateConnectionStatus(false);
    }

    initializeElements() {
        // Gauge elements
        this.speedNeedle = document.getElementById('speedNeedle');
        this.rpmNeedle = document.getElementById('rpmNeedle');
        this.speedValue = document.getElementById('speedValue');
        this.rpmValue = document.getElementById('rpmValue');
        
        // Modern ADAS elements
        this.leftLane = document.getElementById('leftLane');
        this.rightLane = document.getElementById('rightLane');
        this.leftPedestrian = document.getElementById('leftPedestrian');
        this.rightPedestrian = document.getElementById('rightPedestrian');
        this.vehicleBody = document.getElementById('vehicleBody');
        this.globalWarning = document.getElementById('globalWarning');
        this.globalWarningText = document.getElementById('globalWarningText');
        
        // Distance bars
        this.distanceBars = [
            document.getElementById('distBar1'),
            document.getElementById('distBar2'),
            document.getElementById('distBar3'),
            document.getElementById('distBar4'),
            document.getElementById('distBar5')
        ];
        
        // Status elements
        this.connectionDot = document.getElementById('connectionDot');
        this.connectionText = document.getElementById('connectionText');
        this.lastUpdate = document.getElementById('lastUpdate');
    }

    initializeEventListeners() {
        // Dashboard is now view-only, no test controls
    }

    startDataPolling() {
        // Poll for data every 100ms
        setInterval(() => {
            this.fetchVehicleData();
        }, 100);
    }

    async fetchVehicleData() {
        try {
            const response = await fetch('/api/vehicle-data');
            if (response.ok) {
                const data = await response.json();
                this.updateDashboard(data);
                this.updateConnectionStatus(true);
            } else {
                this.updateConnectionStatus(false);
            }
        } catch (error) {
            console.error('Error fetching vehicle data:', error);
            this.updateConnectionStatus(false);
        }
    }

    updateDashboard(data) {
        this.currentData = data;
        
        // Update gauges
        this.updateSpeed(data.speed);
        this.updateRPM(data.rpm);
        
        // Update ADAS systems
        this.updateLaneAssist(data.lane_warning);
        this.updateEmergencyStop(data.emergency_stop);
        this.updatePedestrianDetection(data.pedestrian_warning);
        
        // Update timestamp
        if (data.timestamp) {
            const date = new Date(data.timestamp);
            this.lastUpdate.textContent = date.toLocaleTimeString();
        }
    }

    updateSpeed(speed) {
        // Update digital display
        this.speedValue.textContent = Math.round(speed);
        
        // Update needle (0-200 km/h mapped to 225deg-495deg)
        const angle = 225 + (speed / 200) * 270;
        this.speedNeedle.style.transform = `translateX(-50%) translateY(-100%) rotate(${angle}deg)`;
        
        // Change needle color based on speed
        if (speed > 120) {
            this.speedNeedle.style.background = 'linear-gradient(to top, #ff0000 0%, #ff6600 100%)';
        } else if (speed > 80) {
            this.speedNeedle.style.background = 'linear-gradient(to top, #ffff00 0%, #ffffff 100%)';
        } else {
            this.speedNeedle.style.background = 'linear-gradient(to top, #00ff00 0%, #ffffff 100%)';
        }
    }

    updateRPM(rpm) {
        // Update digital display
        this.rpmValue.textContent = Math.round(rpm);
        
        // Update needle (0-8000 RPM mapped to 225deg-495deg)
        const angle = 225 + (rpm / 8000) * 270;
        this.rpmNeedle.style.transform = `translateX(-50%) translateY(-100%) rotate(${angle}deg)`;
        
        // Change needle color based on RPM
        if (rpm > 6000) {
            this.rpmNeedle.style.background = 'linear-gradient(to top, #ff0000 0%, #ff6600 100%)';
        } else if (rpm > 4000) {
            this.rpmNeedle.style.background = 'linear-gradient(to top, #ffff00 0%, #ffffff 100%)';
        } else {
            this.rpmNeedle.style.background = 'linear-gradient(to top, #00ff00 0%, #ffffff 100%)';
        }
    }

    updateLaneAssist(warning) {
        // Reset lane lines
        this.leftLane.classList.remove('warning');
        this.rightLane.classList.remove('warning');
        
        let hasWarning = false;
        
        if (warning === 'LEFT') {
            this.leftLane.classList.add('warning');
            hasWarning = true;
        } else if (warning === 'RIGHT') {
            this.rightLane.classList.add('warning');
            hasWarning = true;
        }
        
        // Update global warning if there's a lane warning
        this.updateGlobalWarning(hasWarning, hasWarning ? 'LANE WARNING' : null);
    }

    updateEmergencyStop(emergencyData) {
        const isActive = emergencyData.active;
        const distance = emergencyData.distance;
        
        if (isActive) {
            // Update distance bars based on distance
            this.updateDistanceBars(distance);
            this.updateGlobalWarning(true, `OBSTACLE ${distance.toFixed(1)}m`);
        } else {
            this.clearDistanceBars();
            this.updateGlobalWarning(false, null);
        }
    }

    updateDistanceBars(distance) {
        // Clear all bars
        this.distanceBars.forEach(bar => {
            bar.classList.remove('active', 'warning', 'critical');
        });
        
        // Determine how many bars to light based on distance
        // 0-10m: all red (critical)
        // 10-25m: yellow (warning)
        // 25-50m: green (active)
        let activeBarCount = 0;
        let barClass = 'active';
        
        if (distance <= 10) {
            activeBarCount = 5;
            barClass = 'critical';
        } else if (distance <= 25) {
            activeBarCount = Math.max(1, Math.floor(5 - (distance - 10) / 3));
            barClass = 'warning';
        } else if (distance <= 50) {
            activeBarCount = Math.max(1, Math.floor(5 - (distance - 25) / 5));
            barClass = 'active';
        }
        
        // Light up the bars
        for (let i = 0; i < activeBarCount && i < this.distanceBars.length; i++) {
            this.distanceBars[i].classList.add(barClass);
        }
    }

    clearDistanceBars() {
        this.distanceBars.forEach(bar => {
            bar.classList.remove('active', 'warning', 'critical');
        });
    }

    updatePedestrianDetection(warning) {
        // Reset pedestrian indicators
        this.leftPedestrian.classList.remove('detected');
        this.rightPedestrian.classList.remove('detected');
        
        let hasWarning = false;
        
        if (warning === 'LEFT') {
            this.leftPedestrian.classList.add('detected');
            hasWarning = true;
        } else if (warning === 'RIGHT') {
            this.rightPedestrian.classList.add('detected');
            hasWarning = true;
        }
        
        // Update global warning if there's a pedestrian warning
        this.updateGlobalWarning(hasWarning, hasWarning ? 'PEDESTRIAN DETECTED' : null);
    }

    // New function to manage global warning indicator
    updateGlobalWarning(isActive, message) {
        if (isActive) {
            this.globalWarning.classList.add('active');
            this.globalWarningText.textContent = message || 'WARNING';
        } else {
            // Only deactivate if no other warnings are active
            const hasLaneWarning = this.leftLane.classList.contains('warning') || this.rightLane.classList.contains('warning');
            const hasPedestrianWarning = this.leftPedestrian.classList.contains('detected') || this.rightPedestrian.classList.contains('detected');
            const hasObstacleWarning = this.distanceBars.some(bar => bar.classList.contains('critical') || bar.classList.contains('warning'));
            
            if (!hasLaneWarning && !hasPedestrianWarning && !hasObstacleWarning) {
                this.globalWarning.classList.remove('active');
                this.globalWarningText.textContent = 'System OK';
            }
        }
    }

    updateConnectionStatus(connected) {
        this.isConnected = connected;
        this.connectionDot.classList.toggle('active', connected);
        this.connectionText.textContent = connected ? 'Connected' : 'Disconnected';
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    dashboard = new VehicleDashboard();
    
    // Dashboard is now ready for external data
    console.log('Vehicle Dashboard initialized and ready for data');
});