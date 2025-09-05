"""
Simple Demo Script - Minimal version without analytics for testing
"""

import cv2
import numpy as np
import time
import random
import json
from datetime import datetime
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import only essential components
from detector.person_detector import PersonDetector
from queue_management.queue_manager import QueueManager
from visual.interface_manager import InterfaceManager

# Built-in alert system class
class SimpleAlert:
    def __init__(self):
        self.threshold = 5.0
        self.message = "You are late HurryUp!"
        self.counter = 0
        print("✅ Simple Alert System Ready")
    
    def draw_alerts(self, frame, queue_data):
        """Draw alerts directly on frame"""
        self.counter += 1
        
        for queue_id, queue_info in queue_data.items():
            customers = queue_info.get('customers', [])
            if customers:
                customer = customers[0]
                service_start = customer.get('service_start_time')
                if service_start:
                    service_time = time.time() - service_start
                    if service_time >= self.threshold:
                        # Flash every 30 frames
                        flash = (self.counter // 30) % 2 == 0
                        color = (0, 255, 255) if flash else (0, 0, 255)
                        bg = (0, 0, 255) if flash else (0, 0, 0)
                        
                        # Draw alert
                        cv2.rectangle(frame, (50, 80), (600, 150), bg, -1)
                        cv2.rectangle(frame, (50, 80), (600, 150), color, 4)
                        cv2.putText(frame, f"Queue {queue_id}: {self.message}", 
                                   (60, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        cv2.putText(frame, f"Service: {service_time:.1f}s", 
                                   (60, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        # Beep every 60 frames
                        if self.counter % 60 == 0:
                            try:
                                import winsound
                                winsound.Beep(1000, 200)
                            except:
                                print(f"🚨 {self.message} - Queue {queue_id}")
        return frame

class SimpleDemoDataGenerator:
    """Generate simple demo data for testing"""
    
    def __init__(self, frame_width=1280, frame_height=720):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.customers = []
        self.next_customer_id = 1
        
        # Add a few demo customers
        self.customers = [
            {'id': 1, 'x': 150, 'y': 250, 'counter_id': 1},
            {'id': 2, 'x': 170, 'y': 350, 'counter_id': 1},
            {'id': 3, 'x': 450, 'y': 280, 'counter_id': 2}
        ]
    
    def generate_frame(self):
        """Generate a simple demo frame"""
        # Create blank frame
        frame = np.ones((self.frame_height, self.frame_width, 3), dtype=np.uint8) * 50
        
        # Draw simple background
        cv2.putText(frame, "SIMPLE DEMO - QUEUE MANAGEMENT SYSTEM", 
                   (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Draw counter areas
        cv2.rectangle(frame, (100, 200), (300, 600), (100, 100, 100), 2)
        cv2.rectangle(frame, (350, 200), (550, 600), (100, 100, 100), 2)
        
        cv2.putText(frame, "Counter 1", (120, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "Counter 2", (370, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw customers and create detections
        detections = []
        for customer in self.customers:
            x, y = customer['x'], customer['y']
            
            # Draw customer
            cv2.rectangle(frame, (x-20, y-40), (x+20, y), (0, 255, 0), 2)
            cv2.putText(frame, f"C{customer['id']}", (x-15, y-45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            # Create detection
            detection = {
                'bbox': [x-20, y-40, 40, 40],
                'confidence': 0.9,
                'center': [x, y]
            }
            detections.append(detection)
        
        return frame, detections

def run_simple_demo():
    """Run the simple demo"""
    print("Simple Queue Management Demo")
    print("Press 'q' to quit")
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Create components
    print("Initializing components...")
    detector = PersonDetector(config)
    queue_manager = QueueManager(config)
    interface_manager = InterfaceManager(config)
    alert_system = SimpleAlert()
    
    # Create demo data generator
    demo_generator = SimpleDemoDataGenerator()
    
    print("Starting demo...")
    
    try:
        while True:
            # Generate demo frame and detections
            frame, detections = demo_generator.generate_frame()
            
            # Update queue data
            queue_data = queue_manager.update_queues(detections, frame.shape)
            
            # Draw interface
            final_frame = interface_manager.draw_interface(
                frame, detections, queue_data, {'total_customers_served': 5}
            )
            
            # Draw alerts
            final_frame = alert_system.draw_alerts(final_frame, queue_data)
            
            # Display frame
            cv2.imshow('Simple Queue Demo', final_frame)
            
            # Handle key presses
            key = cv2.waitKey(50) & 0xFF
            if key == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    
    finally:
        cv2.destroyAllWindows()
        print("Demo complete!")

if __name__ == "__main__":
    run_simple_demo()
