"""
Simple Alert System (Standalone)
Fixed version that works without complex imports
"""

import cv2
import numpy as np
import time
import threading
import json

class SimpleAlertSystem:
    """Simple alert system for service time monitoring"""
    
    def __init__(self, config=None):
        # Get alert settings from config
        if config and "performance" in config:
            alert_config = config["performance"].get("service_time_alert", {})
            self.threshold_seconds = alert_config.get("threshold_seconds", 5)
            self.alert_message = alert_config.get("message", "You are late HurryUp!")
            self.sound_enabled = alert_config.get("sound_enabled", True)
        else:
            self.threshold_seconds = 5
            self.alert_message = "You are late HurryUp!"
            self.sound_enabled = True
        
        # Active alerts
        self.active_alerts = {}
        self.last_alert_time = {}
        self.flash_state = False
        self.flash_thread = None
        self.flash_running = False
        
        print(f"✅ Simple Alert System initialized")
        print(f"   - Threshold: {self.threshold_seconds} seconds")
        print(f"   - Message: '{self.alert_message}'")
    
    def start_flash_timer(self):
        """Start flashing effect"""
        if not self.flash_running:
            self.flash_running = True
            self.flash_thread = threading.Thread(target=self._flash_worker, daemon=True)
            self.flash_thread.start()
    
    def _flash_worker(self):
        """Background worker for flashing"""
        while self.flash_running and self.active_alerts:
            self.flash_state = not self.flash_state
            time.sleep(0.5)
        self.flash_running = False
    
    def _play_beep(self):
        """Play simple beep sound"""
        try:
            # Try Windows beep
            import winsound
            winsound.Beep(1000, 300)
        except:
            # Fallback: print bell character
            print("\a", end="", flush=True)
    
    def update_service_times(self, queue_data):
        """Check for service time alerts"""
        current_time = time.time()
        new_alerts = set()
        
        for queue_id, queue_info in queue_data.items():
            customers = queue_info.get('customers', [])
            
            # Check current customer (first in queue)
            if customers and len(customers) > 0:
                current_customer = customers[0]
                service_start_time = current_customer.get('service_start_time')
                
                if service_start_time:
                    service_duration = current_time - service_start_time
                    
                    # Check if service time exceeds threshold
                    if service_duration >= self.threshold_seconds:
                        alert_key = f"queue_{queue_id}"
                        new_alerts.add(alert_key)
                        
                        # Check if we should trigger alert
                        last_alert = self.last_alert_time.get(alert_key, 0)
                        if current_time - last_alert >= 2.0:  # Alert every 2 seconds
                            self._trigger_alert(queue_id, service_duration)
                            self.last_alert_time[alert_key] = current_time
                        
                        # Add to active alerts
                        self.active_alerts[alert_key] = {
                            'queue_id': queue_id,
                            'service_duration': service_duration
                        }
        
        # Remove old alerts
        for alert_key in list(self.active_alerts.keys()):
            if alert_key not in new_alerts:
                del self.active_alerts[alert_key]
                if alert_key in self.last_alert_time:
                    del self.last_alert_time[alert_key]
        
        # Start/stop flashing
        if self.active_alerts and not self.flash_running:
            self.start_flash_timer()
        elif not self.active_alerts:
            self.flash_running = False
    
    def _trigger_alert(self, queue_id, service_duration):
        """Trigger alert for queue"""
        print(f"🚨 ALERT: Queue {queue_id} - Service time: {service_duration:.1f}s")
        print(f"   {self.alert_message}")
        
        if self.sound_enabled:
            threading.Thread(target=self._play_beep, daemon=True).start()
    
    def draw_alerts(self, frame, queue_data):
        """Draw visual alerts on frame"""
        if not self.active_alerts:
            return frame
        
        height, width = frame.shape[:2]
        
        for alert_key, alert_info in self.active_alerts.items():
            queue_id = alert_info['queue_id']
            service_duration = alert_info['service_duration']
            
            # Choose color based on flash state
            if self.flash_state:
                color = (0, 255, 255)  # Yellow
                bg_color = (0, 0, 255)  # Red background
            else:
                color = (0, 0, 255)    # Red
                bg_color = (0, 0, 0)   # Black background
            
            # Draw alert at top of screen
            y_pos = 80 + (list(self.active_alerts.keys()).index(alert_key) * 60)
            
            # Background rectangle
            cv2.rectangle(frame, (10, y_pos - 30), (width - 10, y_pos + 20), bg_color, -1)
            cv2.rectangle(frame, (10, y_pos - 30), (width - 10, y_pos + 20), color, 3)
            
            # Alert text
            cv2.putText(frame, f"Queue {queue_id}: {self.alert_message}", 
                       (20, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"Service Time: {service_duration:.1f}s", 
                       (20, y_pos + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame

# Create global alert system instance
def create_alert_system(config_path="config.json"):
    """Create alert system with config"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return SimpleAlertSystem(config)
    except:
        print("Using default alert settings")
        return SimpleAlertSystem()

# For compatibility
AlertSystem = SimpleAlertSystem
