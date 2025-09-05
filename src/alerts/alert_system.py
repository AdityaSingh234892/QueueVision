"""
Alert System Module
Handles visual and audio alerts for the queue management system
"""

import cv2
import numpy as np
import time
import threading
from datetime import datetime
import winsound  # For Windows sound alerts
import sys
import os

class AlertSystem:
    """Manages visual and audio alerts for the queue management system"""
    
    def __init__(self, config):
        self.config = config
        self.performance_config = config.get("performance", {})
        self.alert_config = self.performance_config.get("service_time_alert", {})
        
        # Alert settings
        self.enabled = self.alert_config.get("enabled", True)
        self.threshold_seconds = self.alert_config.get("threshold_seconds", 5)
        self.alert_message = self.alert_config.get("message", "You are late HurryUp!")
        self.sound_enabled = self.alert_config.get("sound_enabled", True)
        self.visual_flash = self.alert_config.get("visual_flash", True)
        self.repeat_interval = self.alert_config.get("repeat_interval", 2)
        
        # Active alerts tracking
        self.active_alerts = {}
        self.last_alert_time = {}
        self.flash_state = False
        self.flash_thread = None
        self.flash_running = False
        
        # Visual settings
        self.alert_color = (0, 0, 255)  # Red
        self.flash_color = (0, 255, 255)  # Yellow
        self.text_size = 1.2
        self.text_thickness = 3
        
        print("✅ Alert System initialized")
        print(f"   - Threshold: {self.threshold_seconds} seconds")
        print(f"   - Message: '{self.alert_message}'")
        print(f"   - Sound: {'ON' if self.sound_enabled else 'OFF'}")
    
    def start_flash_timer(self):
        """Start the flash timer for visual alerts"""
        if not self.flash_running:
            self.flash_running = True
            self.flash_thread = threading.Thread(target=self._flash_worker, daemon=True)
            self.flash_thread.start()
    
    def _flash_worker(self):
        """Background worker for flashing alerts"""
        while self.flash_running and self.active_alerts:
            self.flash_state = not self.flash_state
            time.sleep(0.5)  # Flash every 500ms
        self.flash_running = False
    
    def update_service_times(self, queue_data):
        """Update service times and check for alerts"""
        if not self.enabled:
            return
        
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
                        alert_key = f"queue_{queue_id}_service"
                        new_alerts.add(alert_key)
                        
                        # Check if we should trigger alert (based on repeat interval)
                        last_alert = self.last_alert_time.get(alert_key, 0)
                        if current_time - last_alert >= self.repeat_interval:
                            self._trigger_alert(queue_id, service_duration)
                            self.last_alert_time[alert_key] = current_time
                        
                        # Add to active alerts
                        self.active_alerts[alert_key] = {
                            'queue_id': queue_id,
                            'service_duration': service_duration,
                            'start_time': current_time
                        }
        
        # Remove old alerts
        for alert_key in list(self.active_alerts.keys()):
            if alert_key not in new_alerts:
                del self.active_alerts[alert_key]
                if alert_key in self.last_alert_time:
                    del self.last_alert_time[alert_key]
        
        # Start/stop flashing based on active alerts
        if self.active_alerts and not self.flash_running:
            self.start_flash_timer()
        elif not self.active_alerts:
            self.flash_running = False
    
    def _trigger_alert(self, queue_id, service_duration):
        """Trigger alert for specific queue"""
        print(f"🚨 ALERT: Queue {queue_id} - Service time: {service_duration:.1f}s")
        print(f"   Message: {self.alert_message}")
        
        # Play sound alert
        if self.sound_enabled:
            self._play_sound_alert()
    
    def _play_sound_alert(self):
        """Play sound alert (Windows)"""
        try:
            # Use Windows system beep
            threading.Thread(target=lambda: winsound.Beep(1000, 500), daemon=True).start()
        except Exception as e:
            # Fallback: print beep character
            print("\a")  # ASCII bell character
    
    def draw_alerts(self, frame, queue_data):
        """Draw visual alerts on frame"""
        if not self.enabled or not self.active_alerts:
            return frame
        
        height, width = frame.shape[:2]
        
        for alert_key, alert_info in self.active_alerts.items():
            queue_id = alert_info['queue_id']
            service_duration = alert_info['service_duration']
            
            # Get counter position if available
            counter_config = self.config.get("counters", {})
            counter_positions = counter_config.get("counter_positions", {})
            
            if str(queue_id) in counter_positions:
                pos = counter_positions[str(queue_id)]
                x, y, w, h = pos['x'], pos['y'], pos['width'], pos['height']
                
                # Draw flashing border around counter
                if self.visual_flash and self.flash_state:
                    cv2.rectangle(frame, (x-5, y-5), (x+w+5, y+h+5), self.flash_color, 5)
                
                # Draw alert message
                message = self.alert_message
                time_text = f"Service: {service_duration:.1f}s"
                
                # Choose color based on flash state
                text_color = self.flash_color if self.flash_state else self.alert_color
                
                # Draw background rectangle for text
                text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, self.text_size, self.text_thickness)[0]
                bg_x1, bg_y1 = x, y - 60
                bg_x2, bg_y2 = x + max(text_size[0], 200) + 20, y - 10
                
                cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
                cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), text_color, 2)
                
                # Draw alert text
                cv2.putText(frame, message, (x + 10, y - 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
                cv2.putText(frame, time_text, (x + 10, y - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            else:
                # Draw alert at top of screen if no counter position
                y_pos = 100 + (list(self.active_alerts.keys()).index(alert_key) * 80)
                
                # Background
                cv2.rectangle(frame, (10, y_pos - 40), (width - 10, y_pos + 20), (0, 0, 0), -1)
                cv2.rectangle(frame, (10, y_pos - 40), (width - 10, y_pos + 20), self.alert_color, 2)
                
                # Text
                text_color = self.flash_color if self.flash_state else self.alert_color
                cv2.putText(frame, f"Queue {queue_id}: {self.alert_message}", (20, y_pos - 15),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
                cv2.putText(frame, f"Service Time: {service_duration:.1f}s", (20, y_pos + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        
        return frame
    
    def get_alert_status(self):
        """Get current alert status"""
        return {
            'active_alerts': len(self.active_alerts),
            'alerts': self.active_alerts.copy()
        }
    
    def clear_alerts(self):
        """Clear all active alerts"""
        self.active_alerts.clear()
        self.last_alert_time.clear()
        self.flash_running = False
        print("🔕 All alerts cleared")
    
    def set_threshold(self, seconds):
        """Update alert threshold"""
        self.threshold_seconds = seconds
        print(f"⏰ Alert threshold updated to {seconds} seconds")
    
    def toggle_sound(self):
        """Toggle sound alerts on/off"""
        self.sound_enabled = not self.sound_enabled
        print(f"🔊 Sound alerts: {'ON' if self.sound_enabled else 'OFF'}")
        return self.sound_enabled
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.flash_running = False
