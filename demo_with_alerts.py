"""
Full Demo with Alerts
Complete demonstration of queue management with 5-second alerts
"""

import cv2
import numpy as np
import time
import json
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from detector.person_detector import PersonDetector
from queue_management.queue_manager import QueueManager
from visual.interface_manager import InterfaceManager
from alerts.alert_system import AlertSystem

def run_full_demo():
    """Run the complete demo with alerts"""
    print("🏪 Queue Management System with Alerts")
    print("=" * 40)
    print("Features:")
    print("✅ Person detection")
    print("✅ Queue management")
    print("✅ Visual separation lines")
    print("✅ 5-second service alerts")
    print("✅ Sound notifications")
    print()
    print("🎮 Controls:")
    print("   Q - Quit")
    print("   S - Toggle sound alerts")
    print("   C - Clear all alerts")
    print("   SPACE - Add test customer")
    print()
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found! Run setup_system.py first.")
        return
    
    # Create components
    print("🔧 Initializing components...")
    detector = PersonDetector(config)
    queue_manager = QueueManager(config)
    interface_manager = InterfaceManager(config)
    alert_system = AlertSystem(config)
    
    # Create demo frame
    frame_width, frame_height = 1280, 720
    
    # Test customers for demo
    test_customers = []
    customer_id = 1
    
    print("🚀 Starting demo...")
    print("   Simulating customers with different service times...")
    print("   Watch for alerts after 5 seconds of service!")
    
    try:
        frame_count = 0
        while True:
            # Create base frame
            frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            frame[:] = (40, 40, 40)  # Dark gray background
            
            # Add title
            cv2.putText(frame, "QUEUE MANAGEMENT SYSTEM - LIVE DEMO", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Add counter visualization from config
            counter_positions = config.get('counters', {}).get('counter_positions', {})
            
            # Draw configured counters
            for counter_id, pos in counter_positions.items():
                x, y, w, h = pos['x'], pos['y'], pos['width'], pos['height']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 2)
                cv2.putText(frame, f"Counter {counter_id}", (x + 10, y + 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Simulate detections
            detections = []
            
            # Add test customer every 10 frames
            if frame_count % 10 == 0 and len(test_customers) < 5:
                # Add customer to queue 1
                customer_x = 250 + len(test_customers) * 80
                customer_y = 300
                
                detection = {
                    'person_id': f'person_{customer_id}',
                    'bbox': [customer_x, customer_y, 60, 150],
                    'confidence': 0.9,
                    'center': (customer_x + 30, customer_y + 75)
                }
                test_customers.append(detection)
                customer_id += 1
            
            detections = test_customers.copy()
            
            # Update queue management
            queue_data = queue_manager.update_queues(detections, frame.shape)
            
            # Update alert system
            alert_system.update_service_times(queue_data)
            
            # Draw interface
            annotated_frame = interface_manager.draw_interface(
                frame, detections, queue_data, {
                    'total_customers_served': customer_id - 1,
                    'average_wait_time': 45.2,
                    'system_efficiency': 85.4
                }
            )
            
            # Draw alerts
            annotated_frame = alert_system.draw_alerts(annotated_frame, queue_data)
            
            # Add demo info
            info_y = frame_height - 120
            cv2.putText(annotated_frame, "DEMO INFO:", (20, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            cv2.putText(annotated_frame, f"Frame: {frame_count}", (20, info_y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(annotated_frame, f"Test Customers: {len(test_customers)}", (20, info_y + 45),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Alert status
            status = alert_system.get_alert_status()
            if status['active_alerts'] > 0:
                cv2.putText(annotated_frame, f"🚨 ACTIVE ALERTS: {status['active_alerts']}", (20, info_y + 65),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Show frame
            cv2.imshow('Queue Management Demo with Alerts', annotated_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(100) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                sound_status = alert_system.toggle_sound()
                print(f"🔊 Sound alerts: {'ON' if sound_status else 'OFF'}")
            elif key == ord('c'):
                alert_system.clear_alerts()
                print("🔕 All alerts cleared")
            elif key == ord(' '):  # Space bar
                # Add a new test customer
                if len(test_customers) < 8:
                    customer_x = 250 + len(test_customers) * 60
                    customer_y = 300 + (len(test_customers) % 3) * 80
                    
                    detection = {
                        'person_id': f'person_{customer_id}',
                        'bbox': [customer_x, customer_y, 60, 150],
                        'confidence': 0.9,
                        'center': (customer_x + 30, customer_y + 75)
                    }
                    test_customers.append(detection)
                    customer_id += 1
                    print(f"➕ Added customer {customer_id - 1}")
            
            frame_count += 1
            
            # Remove customers occasionally to simulate completion
            if frame_count % 100 == 0 and test_customers:
                removed = test_customers.pop(0)
                print(f"✅ Customer {removed['person_id']} completed service")
    
    except KeyboardInterrupt:
        print("\n⏹️ Demo stopped by user")
    
    finally:
        cv2.destroyAllWindows()
        print("Demo complete! 🎉")
        print("\nAlert system features demonstrated:")
        print("✅ 5-second service time threshold")
        print("✅ Visual flashing alerts")
        print("✅ Audio notification (beep)")
        print("✅ Custom message: 'You are late HurryUp!'")

if __name__ == "__main__":
    run_full_demo()
