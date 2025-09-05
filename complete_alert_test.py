"""
Complete Alert System Test
Tests all alert functionality including integration with queue management
"""

import cv2
import numpy as np
import time
import json
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.dirname(__file__))

from simple_alert_system import SimpleAlertSystem
from detector.person_detector import PersonDetector
from queue_management.queue_manager import QueueManager
from visual.interface_manager import InterfaceManager

def test_complete_system():
    """Test complete system with alerts"""
    print("🧪 Complete Alert System Test")
    print("=" * 40)
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize all components
    print("Initializing components...")
    detector = PersonDetector(config)
    queue_manager = QueueManager(config)
    interface_manager = InterfaceManager(config)
    alert_system = SimpleAlertSystem(config)
    
    # Create test frame
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    frame[:] = (40, 40, 40)  # Dark gray background
    
    # Add title
    cv2.putText(frame, "COMPLETE ALERT SYSTEM TEST", (50, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Simulate customer detections
    detections = [
        {
            'bbox': [300, 200, 100, 180],  # x, y, w, h
            'confidence': 0.9,
            'person_id': 'test_customer_1'
        }
    ]
    
    print("\nRunning complete system test...")
    print("- Customer will be detected and tracked")
    print("- Service time will be monitored") 
    print("- Alert should trigger after 5 seconds")
    print("\nControls:")
    print("- 'Q' to quit")
    print("- 'R' to reset service time")
    print("- 'S' to toggle sound")
    
    try:
        start_time = time.time()
        
        while True:
            # Create fresh frame
            test_frame = frame.copy()
            
            # Update queue management
            queue_data = queue_manager.update_queues(detections, test_frame.shape)
            
            # Update alerts
            alert_system.update_service_times(queue_data)
            
            # Draw interface
            visual_frame = interface_manager.draw_interface(
                test_frame, detections, queue_data, {'total_customers_served': 0}
            )
            
            # Draw alerts
            final_frame = alert_system.draw_alerts(visual_frame, queue_data)
            
            # Add status information
            elapsed = time.time() - start_time
            cv2.putText(final_frame, f"Test Running: {elapsed:.1f}s", (50, 550),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show queue info
            for queue_id, queue_info in queue_data.items():
                customers = queue_info.get('customers', [])
                if customers:
                    current_customer = customers[0]
                    service_start_time = current_customer.get('service_start_time')
                    if service_start_time:
                        service_duration = time.time() - service_start_time
                        cv2.putText(final_frame, f"Service Time: {service_duration:.1f}s", 
                                   (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        if service_duration >= 5:
                            cv2.putText(final_frame, "ALERT SHOULD BE ACTIVE!", 
                                       (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.putText(final_frame, "Q-Quit | R-Reset | S-Sound", (50, 580),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Display frame
            cv2.imshow('Complete Alert System Test', final_frame)
            
            # Handle keys
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Reset queue manager to restart service timing
                queue_manager = QueueManager(config)
                print("Service time reset")
            elif key == ord('s'):
                alert_system.sound_enabled = not alert_system.sound_enabled
                print(f"Sound: {'ON' if alert_system.sound_enabled else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\nTest interrupted")
    
    finally:
        cv2.destroyAllWindows()
        print("Complete system test finished!")

if __name__ == "__main__":
    test_complete_system()
