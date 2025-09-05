"""
Simple Demo with Built-in Alerts
Working demo with 5-second alerts integrated directly
"""

import cv2
import numpy as np
import time
import json
import random
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from detector.person_detector import PersonDetector
from queue_management.queue_manager import QueueManager
from visual.interface_manager import InterfaceManager

class BuiltInAlertSystem:
    """Built-in alert system that definitely works"""
    
    def __init__(self):
        self.threshold = 5.0  # 5 seconds
        self.message = "You are late HurryUp!"
        self.flash_state = False
        self.last_flash = 0
        self.last_beep = 0
        print("🚨 Built-in Alert System Active (5-second threshold)")
    
    def update_and_draw(self, frame, queue_data):
        """Update alerts and draw them on frame"""
        current_time = time.time()
        
        # Flash every 500ms
        if current_time - self.last_flash > 0.5:
            self.flash_state = not self.flash_state
            self.last_flash = current_time
        
        for queue_id, queue_info in queue_data.items():
            customers = queue_info.get('customers', [])
            
            if customers:
                customer = customers[0]  # Current customer
                service_start = customer.get('service_start_time')
                
                if service_start:
                    service_time = current_time - service_start
                    
                    if service_time >= self.threshold:
                        # Draw flashing alert
                        color = (0, 255, 255) if self.flash_state else (0, 0, 255)
                        bg_color = (0, 0, 255) if self.flash_state else (0, 0, 0)
                        
                        # Alert box
                        cv2.rectangle(frame, (20, 80), (600, 150), bg_color, -1)
                        cv2.rectangle(frame, (20, 80), (600, 150), color, 4)
                        
                        # Alert text
                        cv2.putText(frame, f"Queue {queue_id}: {self.message}", 
                                   (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        cv2.putText(frame, f"Service Time: {service_time:.1f}s", 
                                   (30, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        # Beep every 2 seconds
                        if current_time - self.last_beep > 2.0:
                            try:
                                import winsound
                                winsound.Beep(1000, 300)
                            except:
                                print(f"\a🚨 {self.message} - Queue {queue_id} ({service_time:.1f}s)")
                            self.last_beep = current_time
        
        return frame

def run_demo_with_builtin_alerts():
    """Run demo with built-in alert system"""
    print("🏪 Queue Management Demo with Built-in Alerts")
    print("=" * 50)
    print("✅ 5-second service time alerts")
    print("✅ Visual flashing warnings")
    print("✅ Audio beep notifications")
    print("✅ Message: 'You are late HurryUp!'")
    print()
    print("Press 'q' to quit")
    print()
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        print("Using default configuration")
        config = {"counters": {"total_counters": 1}}
    
    # Initialize components
    print("Initializing components...")
    detector = PersonDetector(config)
    queue_manager = QueueManager(config)
    interface_manager = InterfaceManager(config)
    alert_system = BuiltInAlertSystem()
    
    # Demo data generator
    class DemoGenerator:
        def __init__(self):
            self.frame_count = 0
            self.customers = []
            
        def generate_frame_and_detections(self):
            # Create demo frame
            frame = np.zeros((600, 800, 3), dtype=np.uint8)
            frame[:] = (40, 40, 40)
            
            # Add demo customer every 100 frames
            if self.frame_count % 100 == 0:
                customer_id = f"demo_customer_{len(self.customers)}"
                self.customers.append(customer_id)
            
            # Create detections for active customers
            detections = []
            for i, customer_id in enumerate(self.customers[-3:]):  # Keep last 3
                detection = {
                    'bbox': [200 + i*50, 200 + i*30, 80, 160],
                    'confidence': 0.9,
                    'person_id': customer_id
                }
                detections.append(detection)
            
            self.frame_count += 1
            return frame, detections
    
    demo_gen = DemoGenerator()
    
    print("Starting demo...")
    print("Watch for alerts when service time exceeds 5 seconds!")
    
    try:
        while True:
            # Generate demo data
            frame, detections = demo_gen.generate_frame_and_detections()
            
            # Add title
            cv2.putText(frame, "QUEUE MANAGEMENT WITH ALERTS", (50, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Update queues
            queue_data = queue_manager.update_queues(detections, frame.shape)
            
            # Draw interface
            frame = interface_manager.draw_interface(
                frame, detections, queue_data, {'total_customers_served': 0}
            )
            
            # Update and draw alerts
            frame = alert_system.update_and_draw(frame, queue_data)
            
            # Show status
            cv2.putText(frame, "Press 'Q' to quit", (50, 570),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            
            cv2.imshow('Queue Management with Alerts', frame)
            
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nDemo stopped")
    
    finally:
        cv2.destroyAllWindows()
        print("Demo complete!")

if __name__ == "__main__":
    run_demo_with_builtin_alerts()
