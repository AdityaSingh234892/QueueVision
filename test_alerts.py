"""
Alert System Test
Quick test to verify the 5-second alert system works
"""

import cv2
import numpy as np
import time
import json
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from alerts.alert_system import AlertSystem

def test_alert_system():
    """Test the alert system functionality"""
    print("Testing Alert System")
    print("=" * 30)
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Create alert system
    alert_system = AlertSystem(config)
    
    # Create test frame
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # Simulate queue data with a customer being served for more than 5 seconds
    print("Simulating customer service time...")
    
    # Create customer that started service 6 seconds ago
    service_start_time = time.time() - 6.0
    
    queue_data = {
        1: {
            'queue_id': 1,
            'queue_length': 3,
            'customers': [
                {
                    'person_id': 'customer_1',
                    'queue_id': 1,
                    'service_start_time': service_start_time,
                    'status': 'current'
                },
                {
                    'person_id': 'customer_2',
                    'queue_id': 1,
                    'status': 'waiting'
                },
                {
                    'person_id': 'customer_3',
                    'queue_id': 1,
                    'status': 'waiting'
                }
            ]
        }
    }
    
    print("Running alert system test...")
    print("You should see:")
    print("- Alert message: 'You are late HurryUp!'")
    print("- Flashing visual indicators")
    print("- Sound alert (beep)")
    print()
    print("Press 'q' to quit, 's' to toggle sound")
    
    try:
        while True:
            # Create fresh frame
            test_frame = frame.copy()
            
            # Add some visual context
            cv2.putText(test_frame, "ALERT SYSTEM TEST", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(test_frame, "Customer being served for 6+ seconds", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(test_frame, "Press 'q' to quit, 's' to toggle sound", (50, 550),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            
            # Update service time (simulate continuing service)
            current_time = time.time()
            for customer in queue_data[1]['customers']:
                if customer['status'] == 'current':
                    customer['service_start_time'] = service_start_time
            
            # Update alert system
            alert_system.update_service_times(queue_data)
            
            # Draw alerts
            test_frame = alert_system.draw_alerts(test_frame, queue_data)
            
            # Show status
            status = alert_system.get_alert_status()
            cv2.putText(test_frame, f"Active Alerts: {status['active_alerts']}", (50, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            service_duration = current_time - service_start_time
            cv2.putText(test_frame, f"Service Time: {service_duration:.1f}s", (50, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Display frame
            cv2.imshow('Alert System Test', test_frame)
            
            # Handle key presses
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                sound_status = alert_system.toggle_sound()
                print(f"Sound alerts: {'ON' if sound_status else 'OFF'}")
            elif key == ord('c'):
                alert_system.clear_alerts()
                print("Alerts cleared")
    
    except KeyboardInterrupt:
        print("\nTest interrupted")
    
    finally:
        cv2.destroyAllWindows()
        print("Alert system test complete!")

if __name__ == "__main__":
    test_alert_system()
