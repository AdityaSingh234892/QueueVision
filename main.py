"""
OpenCV Queue Management System - Main Application
Comprehensive retail queue monitoring with visual separation and time tracking
"""

import cv2
import numpy as np
import json
import threading
import time
from datetime import datetime
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from detector.person_detector import PersonDetector
from queue_management.queue_manager import QueueManager
from visual.interface_manager import InterfaceManager
from analytics.performance_monitor import PerformanceMonitor
from analytics.report_generator import ReportGenerator

# Built-in Alert System for Main Application
class MainAlertSystem:
    """Built-in alert system for main.py - guaranteed to work"""
    
    def __init__(self, config=None):
        # Get alert settings from config
        if config and "performance" in config:
            alert_config = config["performance"].get("service_time_alert", {})
            self.threshold = alert_config.get("threshold_seconds", 5)
            self.message = alert_config.get("message", "Please sit - Service taking too long!")
            self.sound_enabled = alert_config.get("sound_enabled", True)
        else:
            self.threshold = 5.0
            self.message = "Please sit - Service taking too long!"
            self.sound_enabled = True
        
        self.counter = 0
        self.last_beep_time = {}
        print(f"🚨 Alert System Integrated")
        print(f"   - Threshold: {self.threshold} seconds")
        print(f"   - Message: '{self.message}'")
        print(f"   - Sound: {'ON' if self.sound_enabled else 'OFF'}")
    
    def draw_alerts(self, frame, queue_data):
        """Draw alerts on frame and handle audio"""
        self.counter += 1
        current_time = time.time()
        
        alert_y = 80  # Start position for alerts
        
        for queue_id, queue_info in queue_data.items():
            customers = queue_info.get('customers', [])
            
            if customers and len(customers) > 0:
                current_customer = customers[0]
                service_start_time = current_customer.get('service_start_time')
                
                if service_start_time:
                    service_duration = current_time - service_start_time
                    
                    if service_duration >= self.threshold:
                        # Flash every 30 frames (about 1 second at 30fps)
                        flash = (self.counter // 30) % 2 == 0
                        
                        if flash:
                            color = (0, 255, 255)  # Yellow
                            bg_color = (0, 0, 255)  # Red
                        else:
                            color = (0, 0, 255)    # Red
                            bg_color = (0, 0, 0)   # Black
                        
                        # Draw alert box
                        height, width = frame.shape[:2]
                        box_width = min(700, width - 40)
                        
                        cv2.rectangle(frame, (20, alert_y), (20 + box_width, alert_y + 80), bg_color, -1)
                        cv2.rectangle(frame, (20, alert_y), (20 + box_width, alert_y + 80), color, 4)
                        
                        # Alert text
                        cv2.putText(frame, f"Queue {queue_id}: {self.message}", 
                                   (30, alert_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        cv2.putText(frame, f"Service Time: {service_duration:.1f} seconds", 
                                   (30, alert_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        # Audio alert every 2 seconds
                        queue_key = f"queue_{queue_id}"
                        last_beep = self.last_beep_time.get(queue_key, 0)
                        
                        if self.sound_enabled and (current_time - last_beep) >= 2.0:
                            try:
                                import winsound
                                winsound.Beep(1000, 300)
                                print(f"🚨 ALERT: Queue {queue_id} - {service_duration:.1f}s - {self.message}")
                            except:
                                print(f"🚨 ALERT: Queue {queue_id} - {service_duration:.1f}s - {self.message}")
                            
                            self.last_beep_time[queue_key] = current_time
                        
                        alert_y += 90  # Move down for next alert
        
        return frame
    
    def toggle_sound(self):
        """Toggle sound alerts on/off"""
        self.sound_enabled = not self.sound_enabled
        print(f"🔊 Sound alerts: {'ON' if self.sound_enabled else 'OFF'}")
        return self.sound_enabled

class QueueManagementSystem:
    """Main application class for the queue management system"""
    
    def __init__(self, config_path="config.json"):
        """Initialize the queue management system"""
        self.config = self.load_config(config_path)
        self.running = False
        
        # Initialize components
        self.detector = PersonDetector(self.config)
        self.queue_manager = QueueManager(self.config)
        self.interface_manager = InterfaceManager(self.config)
        self.performance_monitor = PerformanceMonitor(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.alert_system = MainAlertSystem(self.config)
        
        # Load counter positions from config
        self.counter_positions = self.load_counter_positions()
        
        # Video capture
        self.cap = None
        self.frame_count = 0
        
        # Threading
        self.analytics_thread = None
        self.report_thread = None
        
        print("Queue Management System initialized successfully!")
    
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using default settings.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "detection": {"confidence_threshold": 0.5},
            "queue": {"max_customers_per_queue": 10},
            "visual": {"line_thickness": 3},
            "counters": {
                "total_counters": 4,
                "counter_positions": {
                    "1": {"x": 100, "y": 100, "width": 200, "height": 300},
                    "2": {"x": 350, "y": 100, "width": 200, "height": 300},
                    "3": {"x": 600, "y": 100, "width": 200, "height": 300},
                    "4": {"x": 850, "y": 100, "width": 200, "height": 300}
                },
                "express_lanes": [1, 2],
                "regular_lanes": [3, 4]
            },
            "performance": {"target_service_time": 120},
            "analytics": {"save_interval": 60}
        }
    
    def load_counter_positions(self):
        """Load counter positions from config"""
        counter_config = self.config.get('counters', {})
        positions = counter_config.get('counter_positions', {})
        
        # Convert to the format expected by other components
        counter_positions = {}
        for counter_id, pos in positions.items():
            counter_positions[int(counter_id)] = (
                pos['x'], pos['y'], pos['width'], pos['height']
            )
        
        # If no positions configured, use defaults
        if not counter_positions:
            print("⚠️  No counter positions configured!")
            print("   Run 'python configure_layout.py' or 'python auto_detect_layout.py'")
            print("   to set up counter positions for your video.")
            # Use default positions for now
            counter_positions = {
                1: (100, 100, 200, 300),
                2: (350, 100, 200, 300),
                3: (600, 100, 200, 300),
                4: (850, 100, 200, 300)
            }
        
        return counter_positions
    
    def initialize_camera(self, camera_id=0):
        """Initialize camera capture"""
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {camera_id}")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        return True
    
    def start_background_threads(self):
        """Start background threads for analytics and reporting"""
        self.analytics_thread = threading.Thread(target=self.analytics_worker, daemon=True)
        self.report_thread = threading.Thread(target=self.report_worker, daemon=True)
        
        self.analytics_thread.start()
        self.report_thread.start()
    
    def analytics_worker(self):
        """Background worker for analytics processing"""
        while self.running:
            try:
                # Update performance metrics
                self.performance_monitor.update_metrics()
                
                # Check for alerts
                alerts = self.performance_monitor.check_alerts()
                if alerts:
                    self.interface_manager.add_alerts(alerts)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Analytics worker error: {e}")
    
    def report_worker(self):
        """Background worker for report generation"""
        while self.running:
            try:
                # Generate periodic reports
                self.report_generator.generate_hourly_report()
                
                # Save data
                self.queue_manager.save_queue_data()
                self.performance_monitor.save_performance_data()
                
                time.sleep(self.config["analytics"]["save_interval"])
                
            except Exception as e:
                print(f"Report worker error: {e}")
    
    def process_frame(self, frame):
        """Process a single frame for queue management"""
        self.frame_count += 1
        
        # Detect persons in frame
        detections = self.detector.detect_persons(frame)
        
        # Update queue information
        queue_data = self.queue_manager.update_queues(detections, frame.shape)
        
        # Update performance metrics
        self.performance_monitor.update_frame_data(queue_data, detections)
        
        # Draw visual interface
        annotated_frame = self.interface_manager.draw_interface(
            frame, detections, queue_data, self.performance_monitor.get_current_metrics()
        )
        
        # Draw alerts on top (built-in system handles timing automatically)
        annotated_frame = self.alert_system.draw_alerts(annotated_frame, queue_data)
        
        return annotated_frame
    
    def run(self, camera_id=0, video_path=None):
        """Main application loop"""
        print("Starting Queue Management System...")
        
        # Initialize camera or video
        if video_path:
            self.cap = cv2.VideoCapture(video_path)
        else:
            if not self.initialize_camera(camera_id):
                return
        
        self.running = True
        self.start_background_threads()
        
        print("System running. Press 'q' to quit, 's' to save report, 'r' to reset counters")
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    if video_path:
                        # Restart video for continuous loop
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        print("Error: Could not read frame from camera")
                        break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display frame
                cv2.imshow('Queue Management System', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Shutting down...")
                    break
                elif key == ord('s'):
                    print("Generating manual report...")
                    self.report_generator.generate_manual_report()
                elif key == ord('r'):
                    print("Resetting counters...")
                    self.queue_manager.reset_counters()
                    self.performance_monitor.reset_metrics()
                elif key == ord('a'):
                    # Toggle alert sound
                    self.alert_system.toggle_sound()
                elif key == ord('h'):
                    self.show_help()
                
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
        
        finally:
            self.cleanup()
    
    def show_help(self):
        """Display help information"""
        help_text = """
        Queue Management System Controls:
        
        q - Quit application
        s - Save manual report
        r - Reset all counters
        a - Toggle alert sound ON/OFF
        h - Show this help
        
        Alert Features:
        - 5-second service time threshold
        - Visual flashing alerts (red/yellow)
        - Audio beep notifications
        - Message: "You are late HurryUp!"
        - Automatic detection and tracking
        
        Other Features:
        - Real-time customer detection and tracking
        - Visual queue separation lines
        - Individual service time calculation
        - Performance monitoring and analytics
        - Automated reporting
        """
        print(help_text)
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        # Generate final report
        print("Generating final report...")
        self.report_generator.generate_final_report()
        
        print("Queue Management System shutdown complete.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenCV Queue Management System')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--video', type=str, help='Path to video file (optional)')
    parser.add_argument('--config', type=str, default='config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Create system instance
    system = QueueManagementSystem(args.config)
    
    # Run the system
    system.run(camera_id=args.camera, video_path=args.video)

if __name__ == "__main__":
    main()
