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
        
        // ADAS elements
        this.leftLane = document.getElementById('leftLane');
        this.rightLane = document.getElementById('rightLane');
        this.laneWarning = document.getElementById('laneWarning');
        this.laneWarningText = document.getElementById('laneWarningText');
        
        this.emergencyWarning = document.getElementById('emergencyWarning');
        this.emergencyWarningText = document.getElementById('emergencyWarningText');
        this.obstacleDistance = document.getElementById('obstacleDistance');
        this.obstacleIcon = document.getElementById('obstacleIcon');
        
        this.pedestrianWarning = document.getElementById('pedestrianWarning');
        this.pedestrianWarningText = document.getElementById('pedestrianWarningText');
        this.leftPedLight = document.getElementById('leftPedLight');
        this.rightPedLight = document.getElementById('rightPedLight');
        this.leftPedestrian = document.getElementById('leftPedestrian');
        this.rightPedestrian = document.getElementById('rightPedestrian');
        
        // Status elements
        this.connectionDot = document.getElementById('connectionDot');
        this.connectionText = document.getElementById('connectionText');
        this.lastUpdate = document.getElementById('lastUpdate');
        
        // Test controls
        this.speedSlider = document.getElementById('speedSlider');
        this.rpmSlider = document.getElementById('rpmSlider');
        this.speedDisplay = document.getElementById('speedDisplay');
        this.rpmDisplay = document.getElementById('rpmDisplay');
        this.distanceInput = document.getElementById('distanceInput');
    }

    initializeEventListeners() {
        // Test control sliders
        if (this.speedSlider) {
            this.speedSlider.addEventListener('input', (e) => {
                const speed = parseInt(e.target.value);
                this.speedDisplay.textContent = speed;
                this.updateSpeed(speed);
            });
        }

        if (this.rpmSlider) {
            this.rpmSlider.addEventListener('input', (e) => {
                const rpm = parseInt(e.target.value);
                this.rpmDisplay.textContent = rpm;
                this.updateRPM(rpm);
            });
        }
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
        this.laneWarning.classList.remove('active');
        
        if (warning === 'LEFT') {
            this.leftLane.classList.add('warning');
            this.laneWarning.classList.add('active');
            this.laneWarningText.textContent = 'LEFT LANE WARNING';
        } else if (warning === 'RIGHT') {
            this.rightLane.classList.add('warning');
            this.laneWarning.classList.add('active');
            this.laneWarningText.textContent = 'RIGHT LANE WARNING';
        } else {
            this.laneWarningText.textContent = 'No Warning';
        }
    }

    updateEmergencyStop(emergencyData) {
        const isActive = emergencyData.active;
        const distance = emergencyData.distance;
        
        this.emergencyWarning.classList.toggle('active', isActive);
        this.obstacleIcon.classList.toggle('active', isActive);
        
        if (isActive) {
            this.emergencyWarningText.textContent = `OBSTACLE DETECTED`;
            this.obstacleDistance.textContent = distance.toFixed(1);
            
            // Update distance bars based on distance
            this.updateDistanceBars(distance);
        } else {
            this.emergencyWarningText.textContent = 'No Warning';
            this.obstacleDistance.textContent = '-';
            this.clearDistanceBars();
        }
    }

    updateDistanceBars(distance) {
        const bars = [
            document.getElementById('distBar1'),
            document.getElementById('distBar2'),
            document.getElementById('distBar3'),
            document.getElementById('distBar4'),
            document.getElementById('distBar5')
        ];
        
        // Clear all bars
        bars.forEach(bar => {
            bar.classList.remove('active', 'warning', 'danger');
        });
        
        // Determine how many bars to light based on distance
        // 0-10m: all red (danger)
        // 10-25m: yellow (warning)
        // 25-50m: green (safe)
        let activeBarCount = 0;
        let barClass = 'active';
        
        if (distance <= 10) {
            activeBarCount = 5;
            barClass = 'danger';
        } else if (distance <= 25) {
            activeBarCount = Math.max(1, Math.floor(5 - (distance - 10) / 3));
            barClass = 'warning';
        } else if (distance <= 50) {
            activeBarCount = Math.max(1, Math.floor(5 - (distance - 25) / 5));
            barClass = 'active';
        }
        
        // Light up the bars
        for (let i = 0; i < activeBarCount && i < bars.length; i++) {
            bars[i].classList.add(barClass);
        }
    }

    clearDistanceBars() {
        const bars = [
            document.getElementById('distBar1'),
            document.getElementById('distBar2'),
            document.getElementById('distBar3'),
            document.getElementById('distBar4'),
            document.getElementById('distBar5')
        ];
        
        bars.forEach(bar => {
            bar.classList.remove('active', 'warning', 'danger');
        });
    }

    updatePedestrianDetection(warning) {
        // Reset pedestrian indicators
        this.leftPedLight.classList.remove('active');
        this.rightPedLight.classList.remove('active');
        this.leftPedestrian.classList.remove('warning');
        this.rightPedestrian.classList.remove('warning');
        this.pedestrianWarning.classList.remove('active');
        
        if (warning === 'LEFT') {
            this.leftPedLight.classList.add('active');
            this.leftPedestrian.classList.add('warning');
            this.pedestrianWarning.classList.add('active');
            this.pedestrianWarningText.textContent = 'PEDESTRIAN LEFT';
        } else if (warning === 'RIGHT') {
            this.rightPedLight.classList.add('active');
            this.rightPedestrian.classList.add('warning');
            this.pedestrianWarning.classList.add('active');
            this.pedestrianWarningText.textContent = 'PEDESTRIAN RIGHT';
        } else {
            this.pedestrianWarningText.textContent = 'No Warning';
        }
    }

    updateConnectionStatus(connected) {
        this.isConnected = connected;
        this.connectionDot.classList.toggle('active', connected);
        this.connectionText.textContent = connected ? 'Connected' : 'Disconnected';
    }

    // Test control functions
    async sendLaneWarning(direction) {
        try {
            await fetch('/api/lane-assist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ direction: direction })
            });
        } catch (error) {
            console.error('Error sending lane warning:', error);
        }
    }

    async clearLaneWarning() {
        try {
            await fetch('/api/lane-assist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ direction: null })
            });
        } catch (error) {
            console.error('Error clearing lane warning:', error);
        }
    }

    async sendEmergencyWarning() {
        const distance = parseFloat(this.distanceInput.value) || 0;
        try {
            await fetch('/api/emergency-stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ type: 'OBSTACLE', distance: distance })
            });
        } catch (error) {
            console.error('Error sending emergency warning:', error);
        }
    }

    async clearEmergencyWarning() {
        try {
            await fetch('/api/emergency-stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ type: null, distance: 0 })
            });
        } catch (error) {
            console.error('Error clearing emergency warning:', error);
        }
    }

    async sendPedestrianWarning(direction) {
        try {
            await fetch('/api/pedestrian-detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ direction: direction })
            });
        } catch (error) {
            console.error('Error sending pedestrian warning:', error);
        }
    }

    async clearPedestrianWarning() {
        try {
            await fetch('/api/pedestrian-detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ direction: null })
            });
        } catch (error) {
            console.error('Error clearing pedestrian warning:', error);
        }
    }
}

// Global functions for test controls
let dashboard;

function sendLaneWarning(direction) {
    dashboard.sendLaneWarning(direction);
}

function clearLaneWarning() {
    dashboard.clearLaneWarning();
}

function sendEmergencyWarning() {
    dashboard.sendEmergencyWarning();
}

function clearEmergencyWarning() {
    dashboard.clearEmergencyWarning();
}

function sendPedestrianWarning(direction) {
    dashboard.sendPedestrianWarning(direction);
}

function clearPedestrianWarning() {
    dashboard.clearPedestrianWarning();
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    dashboard = new VehicleDashboard();
    
    // Simulate some initial data for demonstration
    setTimeout(() => {
        dashboard.updateSpeed(45);
        dashboard.updateRPM(2200);
    }, 1000);
});