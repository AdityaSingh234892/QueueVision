"""
Minimal Alert System - Guaranteed Working Version
Simple 5-second service time alert system
"""

import cv2
import time

class MinimalAlertSystem:
    def __init__(self):
        self.threshold = 5  # 5 seconds
        self.message = "You are late HurryUp!"
        self.flash_state = False
        self.last_flash_time = 0
        print("✅ Minimal Alert System Ready (5-second threshold)")
    
    def check_and_draw_alerts(self, frame, queue_data):
        """Check for alerts and draw them"""
        current_time = time.time()
        
        # Flash every 0.5 seconds
        if current_time - self.last_flash_time > 0.5:
            self.flash_state = not self.flash_state
            self.last_flash_time = current_time
        
        alert_count = 0
        
        for queue_id, queue_info in queue_data.items():
            customers = queue_info.get('customers', [])
            
            if customers and len(customers) > 0:
                current_customer = customers[0]
                service_start_time = current_customer.get('service_start_time')
                
                if service_start_time:
                    service_duration = current_time - service_start_time
                    
                    if service_duration >= self.threshold:
                        alert_count += 1
                        
                        # Choose color based on flash state
                        if self.flash_state:
                            color = (0, 255, 255)  # Yellow
                            bg_color = (0, 0, 255)  # Red
                        else:
                            color = (0, 0, 255)    # Red  
                            bg_color = (0, 0, 0)   # Black
                        
                        # Draw alert box
                        y_pos = 60 + (alert_count * 80)
                        
                        # Background
                        cv2.rectangle(frame, (10, y_pos), (600, y_pos + 60), bg_color, -1)
                        cv2.rectangle(frame, (10, y_pos), (600, y_pos + 60), color, 3)
                        
                        # Alert text
                        cv2.putText(frame, f"Queue {queue_id}: {self.message}", 
                                   (20, y_pos + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                        cv2.putText(frame, f"Service Time: {service_duration:.1f}s", 
                                   (20, y_pos + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        # Sound alert (every 2 seconds)
                        if int(service_duration) % 2 == 0 and service_duration != int(service_duration):
                            try:
                                import winsound
                                winsound.Beep(1000, 200)
                            except:
                                print(f"\a🚨 ALERT: Queue {queue_id} - {self.message}")
        
        return frame

# Test function
def test_minimal_alerts():
    """Test the minimal alert system"""
    print("Testing Minimal Alert System...")
    
    alert_system = MinimalAlertSystem()
    
    # Create test frame
    frame = cv2.imread("test_frame.jpg") if cv2.imread("test_frame.jpg") is not None else \
            np.zeros((500, 800, 3), dtype=np.uint8)
    
    # Simulate customer that started service 6 seconds ago
    test_queue_data = {
        1: {
            'customers': [
                {
                    'person_id': 'test_customer',
                    'service_start_time': time.time() - 6.0,  # 6 seconds ago
                    'status': 'current'
                }
            ]
        }
    }
    
    print("Running test - should show alert...")
    
    for i in range(10):
        test_frame = frame.copy()
        
        # Add title
        cv2.putText(test_frame, "MINIMAL ALERT TEST", (50, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Check and draw alerts
        result_frame = alert_system.check_and_draw_alerts(test_frame, test_queue_data)
        
        cv2.imshow('Minimal Alert Test', result_frame)
        if cv2.waitKey(500) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    print("Test complete!")

if __name__ == "__main__":
    import numpy as np
    test_minimal_alerts()
