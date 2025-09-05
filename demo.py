"""
Demo Script for Queue Management System
Demonstrates the system with simulated data when no camera is available
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

from main import QueueManagementSystem

class DemoDataGenerator:
    """Generate demo data for testing the queue management system"""
    
    def __init__(self, frame_width=1280, frame_height=720):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = 0
        
        # Simulate customers
        self.customers = []
        self.next_customer_id = 1
        
        # Counter positions (matching config.json)
        self.counter_positions = {
            "1": {"x": 100, "y": 200, "width": 200, "height": 400},
            "2": {"x": 350, "y": 200, "width": 200, "height": 400},
            "3": {"x": 600, "y": 200, "width": 200, "height": 400},
            "4": {"x": 850, "y": 200, "width": 200, "height": 400}
        }
        
        # Initialize some demo customers
        self.initialize_demo_customers()
    
    def initialize_demo_customers(self):
        """Initialize demo customers in different queues"""
        for counter_id, pos in self.counter_positions.items():
            # Add 2-4 customers per counter
            num_customers = random.randint(2, 4)
            
            for i in range(num_customers):
                customer_x = pos["x"] + pos["width"] // 2 + random.randint(-30, 30)
                customer_y = pos["y"] + (i + 1) * 80 + random.randint(-20, 20)
                
                self.customers.append({
                    'id': self.next_customer_id,
                    'x': customer_x,
                    'y': customer_y,
                    'counter_id': int(counter_id),
                    'service_start': None if i > 0 else time.time(),
                    'status': 'current' if i == 0 else 'waiting',
                    'target_y': customer_y,
                    'move_speed': random.uniform(0.5, 2.0)
                })
                self.next_customer_id += 1
    
    def generate_frame(self):
        """Generate a demo frame with simulated customers"""
        # Create blank frame
        frame = np.ones((self.frame_height, self.frame_width, 3), dtype=np.uint8) * 50
        
        # Draw store background
        self.draw_store_background(frame)
        
        # Update customer positions
        self.update_customer_positions()
        
        # Draw customers
        detections = self.draw_customers(frame)
        
        # Add some noise and movement
        self.add_realistic_effects(frame)
        
        self.frame_count += 1
        return frame, detections
    
    def draw_store_background(self, frame):
        """Draw store background elements"""
        # Draw checkout counters
        for counter_id, pos in self.counter_positions.items():
            x, y, w, h = pos["x"], pos["y"], pos["width"], pos["height"]
            
            # Counter area
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 2)
            
            # Checkout desk (top part)
            cv2.rectangle(frame, (x, y), (x + w, y + 50), (150, 150, 150), -1)
            
            # Counter label
            label = f"Counter {counter_id}"
            cv2.putText(frame, label, (x + 10, y + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Express lane indicator
            if counter_id in ["1", "2"]:
                cv2.putText(frame, "EXPRESS", (x + 10, y + h - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw floor markings
        for y in range(200, 700, 100):
            cv2.line(frame, (50, y), (1230, y), (80, 80, 80), 1)
        
        # Add store name
        cv2.putText(frame, "DEMO RETAIL STORE - QUEUE MANAGEMENT SYSTEM", 
                   (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    def update_customer_positions(self):
        """Update customer positions to simulate movement"""
        for customer in self.customers:
            # Simulate queue movement
            if customer['status'] == 'waiting':
                # Move customers forward occasionally
                if random.random() < 0.01:  # 1% chance per frame
                    customer['y'] -= 5
            
            elif customer['status'] == 'current':
                # Current customer might leave after some time
                if customer['service_start'] and time.time() - customer['service_start'] > random.uniform(30, 120):
                    customer['status'] = 'leaving'
                    customer['target_y'] = customer['y'] - 100
        
        # Remove customers who have left
        self.customers = [c for c in self.customers if c['status'] != 'left']
        
        # Occasionally add new customers
        if random.random() < 0.005:  # 0.5% chance per frame
            self.add_random_customer()
        
        # Promote waiting customers to current when needed
        self.promote_waiting_customers()
    
    def add_random_customer(self):
        """Add a new random customer to a queue"""
        counter_id = random.choice(list(self.counter_positions.keys()))
        pos = self.counter_positions[counter_id]
        
        # Find the last customer in this queue
        queue_customers = [c for c in self.customers if c['counter_id'] == int(counter_id)]
        if queue_customers:
            last_y = max(c['y'] for c in queue_customers)
            new_y = last_y + 80
        else:
            new_y = pos["y"] + 100
        
        new_customer = {
            'id': self.next_customer_id,
            'x': pos["x"] + pos["width"] // 2 + random.randint(-30, 30),
            'y': new_y,
            'counter_id': int(counter_id),
            'service_start': None,
            'status': 'waiting',
            'target_y': new_y,
            'move_speed': random.uniform(0.5, 2.0)
        }
        
        self.customers.append(new_customer)
        self.next_customer_id += 1
    
    def promote_waiting_customers(self):
        """Promote waiting customers to current when no one is being served"""
        for counter_id in self.counter_positions.keys():
            counter_customers = [c for c in self.customers if c['counter_id'] == int(counter_id)]
            
            # Check if there's a current customer
            current_customers = [c for c in counter_customers if c['status'] == 'current']
            
            if not current_customers:
                # Find the next waiting customer
                waiting_customers = [c for c in counter_customers if c['status'] == 'waiting']
                if waiting_customers:
                    # Promote the first waiting customer
                    next_customer = min(waiting_customers, key=lambda c: c['y'])
                    next_customer['status'] = 'current'
                    next_customer['service_start'] = time.time()
    
    def draw_customers(self, frame):
        """Draw customers on the frame and return detection data"""
        detections = []
        
        for customer in self.customers:
            x, y = int(customer['x']), int(customer['y'])
            
            # Customer bounding box (simulating person detection)
            bbox_width = 40
            bbox_height = 80
            bbox_x = x - bbox_width // 2
            bbox_y = y - bbox_height
            
            # Choose color based on status
            if customer['status'] == 'current':
                color = (0, 255, 0)  # Green for current customer
            elif customer['status'] == 'waiting':
                color = (0, 0, 255)  # Red for waiting
            else:
                color = (128, 128, 128)  # Gray for leaving
            
            # Draw customer representation
            cv2.rectangle(frame, (bbox_x, bbox_y), 
                         (bbox_x + bbox_width, bbox_y + bbox_height), color, 2)
            
            # Draw customer center point
            cv2.circle(frame, (x, y), 5, color, -1)
            
            # Add customer ID
            cv2.putText(frame, f"C{customer['id']}", (bbox_x, bbox_y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Create detection data
            detection = {
                'bbox': [bbox_x, bbox_y, bbox_width, bbox_height],
                'confidence': random.uniform(0.7, 0.95),
                'center': [x, y],
                'person_id': customer['id']
            }
            detections.append(detection)
        
        return detections
    
    def add_realistic_effects(self, frame):
        """Add realistic camera effects"""
        # Add slight noise
        noise = np.random.randint(-10, 10, frame.shape, dtype=np.int16)
        frame_int = frame.astype(np.int16)
        frame_with_noise = np.clip(frame_int + noise, 0, 255).astype(np.uint8)
        frame[:] = frame_with_noise
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"DEMO CAM 01 - {timestamp}", (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

class DemoQueueSystem(QueueManagementSystem):
    """Demo version of the queue management system"""
    
    def __init__(self):
        super().__init__()
        self.demo_generator = DemoDataGenerator()
        print("Demo Queue Management System initialized")
    
    def run_demo(self):
        """Run the demo with simulated data"""
        print("Starting Demo Mode...")
        print("Demo simulates a retail store with 4 checkout counters")
        print("Customers will move through queues automatically")
        print("Press 'q' to quit, 's' to save report, 'r' to reset counters")
        
        self.running = True
        self.start_background_threads()
        
        try:
            while self.running:
                # Generate demo frame and detections
                frame, detections = self.demo_generator.generate_frame()
                
                # Process frame through the queue management system
                processed_frame = self.process_frame(frame)
                
                # Override detections with demo data
                queue_data = self.queue_manager.update_queues(detections, frame.shape)
                
                # Draw the interface with demo data
                final_frame = self.interface_manager.draw_interface(
                    frame, detections, queue_data, 
                    self.performance_monitor.get_current_metrics()
                )
                
                # Display frame
                cv2.imshow('Queue Management System - DEMO MODE', final_frame)
                
                # Handle key presses
                key = cv2.waitKey(50) & 0xFF  # Slower for demo
                if key == ord('q'):
                    print("Shutting down demo...")
                    break
                elif key == ord('s'):
                    print("Generating demo report...")
                    self.report_generator.generate_manual_report()
                elif key == ord('r'):
                    print("Resetting demo counters...")
                    self.queue_manager.reset_counters()
                    self.performance_monitor.reset_metrics()
                    self.demo_generator.initialize_demo_customers()
                elif key == ord('h'):
                    self.show_demo_help()
                elif key == ord('n'):
                    print("Adding new customers...")
                    for _ in range(3):
                        self.demo_generator.add_random_customer()
                
        except KeyboardInterrupt:
            print("\nDemo shutdown requested by user")
        
        finally:
            self.cleanup()
    
    def show_demo_help(self):
        """Show demo-specific help"""
        help_text = """
        Demo Queue Management System Controls:
        
        q - Quit demo
        s - Save demo report
        r - Reset counters and customers
        n - Add new random customers
        h - Show this help
        
        Demo Features:
        - Simulated customers move through queues
        - Automatic service completion
        - Real-time metrics and analytics
        - Visual separation lines and overlays
        """
        print(help_text)

def main():
    """Main demo function"""
    print("OpenCV Queue Management System - Demo Mode")
    print("=" * 50)
    
    try:
        # Create and run demo system
        demo_system = DemoQueueSystem()
        demo_system.run_demo()
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
