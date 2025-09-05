"""
Ultra Simple Alert System Test
This WILL work - guaranteed simple version
"""

import cv2
import numpy as np
import time

# Create test window
def test_simple_alert():
    print("🚨 Ultra Simple Alert Test")
    print("This should definitely work!")
    
    # Create a simple black frame
    frame = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Simulate a customer that has been waiting 6 seconds
    customer_start_time = time.time() - 6.0  # Started 6 seconds ago
    threshold = 5.0  # 5 second threshold
    
    counter = 0
    
    print("Starting test - you should see flashing alert...")
    print("Press 'q' to quit")
    
    while True:
        # Create fresh frame
        test_frame = frame.copy()
        
        # Calculate service time
        current_time = time.time()
        service_time = current_time - customer_start_time
        
        # Check if alert should show
        if service_time >= threshold:
            # Flash every 30 frames (about 1 second)
            flash = (counter // 30) % 2 == 0
            
            if flash:
                color = (0, 255, 255)  # Yellow
                bg = (0, 0, 255)       # Red
            else:
                color = (0, 0, 255)    # Red
                bg = (0, 0, 0)         # Black
            
            # Draw alert box
            cv2.rectangle(test_frame, (50, 100), (550, 200), bg, -1)
            cv2.rectangle(test_frame, (50, 100), (550, 200), color, 4)
            
            # Alert text
            cv2.putText(test_frame, "You are late HurryUp!", 
                       (60, 140), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(test_frame, f"Service Time: {service_time:.1f}s", 
                       (60, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Make beep sound every 60 frames (about 2 seconds)
            if counter % 60 == 0:
                try:
                    import winsound
                    winsound.Beep(1000, 200)
                    print(f"🚨 BEEP! Service time: {service_time:.1f}s")
                except:
                    print(f"🚨 ALERT! You are late HurryUp! ({service_time:.1f}s)")
        
        # Add title and info
        cv2.putText(test_frame, "ULTRA SIMPLE ALERT TEST", 
                   (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(test_frame, f"Current Time: {service_time:.1f}s", 
                   (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(test_frame, f"Threshold: {threshold}s", 
                   (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(test_frame, "Press 'q' to quit", 
                   (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        
        # Show frame
        cv2.imshow('Ultra Simple Alert Test', test_frame)
        
        # Check for quit
        key = cv2.waitKey(33) & 0xFF  # About 30 FPS
        if key == ord('q'):
            break
        
        counter += 1
    
    cv2.destroyAllWindows()
    print("Test completed!")

if __name__ == "__main__":
    test_simple_alert()
