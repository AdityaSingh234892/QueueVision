"""
Working Alert System Demo
Tests the 5-second service time alert with simulated customers
"""

import cv2
import numpy as np
import time
import json
import random
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import components
from simple_alert_system import SimpleAlertSystem

def create_test_frame():
    """Create a test frame with counter layout"""
    frame = np.zeros((600, 1000, 3), dtype=np.uint8)
    
    # Draw background
    frame[:] = (50, 50, 50)
    
    # Draw counter area based on config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        counter_positions = config.get('counters', {}).get('counter_positions', {})
        
        for counter_id, pos in counter_positions.items():
            x, y, w, h = pos['x'], pos['y'], pos['width'], pos['height']
            
            # Scale down for demo if needed
            if w > 800 or h > 500:
                scale = min(800/w, 500/h)
                x = int(x * scale)
                y = int(y * scale)
                w = int(w * scale)
                h = int(h * scale)
            
            # Draw counter
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 2)
            cv2.putText(frame, f"Counter {counter_id}", (x + 10, y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw vertical service line
            service_x = x + w // 3
            cv2.line(frame, (service_x, y), (service_x, y + h), (0, 255, 0), 3)
            cv2.putText(frame, "Service", (service_x + 5, y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    except:
        # Default counter if config not available
        cv2.rectangle(frame, (100, 100), (400, 400), (100, 100, 100), 2)
        cv2.putText(frame, "Counter 1", (110, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.line(frame, (200, 100), (200, 400), (0, 255, 0), 3)
    
    return frame

def run_alert_demo():
    """Run the alert system demo"""
    print("🚨 Alert System Demo")
    print("=" * 30)
    print("Testing 5-second service time alerts")
    print()
    
    # Create alert system
    alert_system = SimpleAlertSystem()
    
    # Create simulated customer data
    customers = [
        {
            'person_id': 'customer_1',
            'queue_id': 1,
            'service_start_time': time.time() - 6,  # Started 6 seconds ago (should alert)
            'status': 'current'
        },
        {
            'person_id': 'customer_2', 
            'queue_id': 1,
            'status': 'waiting'
        }
    ]
    
    queue_data = {
        1: {
            'queue_id': 1,
            'queue_length': 2,
            'customers': customers
        }
    }
    
    print("Controls:")
    print("- 'Q' to quit")
    print("- 'S' to toggle sound")
    print("- 'R' to reset customer (new service time)")
    print("- 'A' to add 2 seconds to service time")
    print()
    
    try:
        while True:
            # Create frame
            frame = create_test_frame()
            
            # Add instructions
            cv2.putText(frame, "ALERT SYSTEM DEMO", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Calculate current service time
            current_time = time.time()
            service_duration = current_time - customers[0]['service_start_time']
            
            cv2.putText(frame, f"Service Time: {service_duration:.1f}s", (50, 500),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Threshold: {alert_system.threshold_seconds}s", (50, 530),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            if service_duration >= alert_system.threshold_seconds:
                cv2.putText(frame, "SHOULD SHOW ALERT!", (50, 560),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Update alert system
            alert_system.update_service_times(queue_data)
            
            # Draw alerts
            frame = alert_system.draw_alerts(frame, queue_data)
            
            # Show controls
            cv2.putText(frame, "Q-Quit | S-Sound | R-Reset | A-Add Time", (50, 580),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Display frame
            cv2.imshow('Alert System Demo', frame)
            
            # Handle keys
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                alert_system.sound_enabled = not alert_system.sound_enabled
                print(f"Sound: {'ON' if alert_system.sound_enabled else 'OFF'}")
            elif key == ord('r'):
                # Reset customer service time
                customers[0]['service_start_time'] = time.time()
                print("Customer service time reset")
            elif key == ord('a'):
                # Add 2 seconds to service time
                customers[0]['service_start_time'] -= 2
                print("Added 2 seconds to service time")
    
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    
    finally:
        cv2.destroyAllWindows()
        print("Alert demo complete!")

if __name__ == "__main__":
    run_alert_demo()
