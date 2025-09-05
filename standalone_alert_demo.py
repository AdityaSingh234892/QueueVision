"""
Standalone Alert Demo - No Dependencies
Complete working alert system demonstration
"""

import cv2
import numpy as np
import time
import json

class StandaloneAlertDemo:
    def __init__(self):
        self.threshold = 5.0
        self.message = "You are late HurryUp!"
        self.customers = []
        self.counter = 0
        
        # Load counter positions from config if available
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            self.counter_positions = config.get('counters', {}).get('counter_positions', {})
        except:
            # Default counter position
            self.counter_positions = {'1': {'x': 200, 'y': 150, 'width': 400, 'height': 300}}
        
        print("🚨 Standalone Alert Demo")
        print(f"✅ Alert threshold: {self.threshold} seconds")
        print(f"✅ Alert message: '{self.message}'")
        print("✅ Visual flashing: ON")
        print("✅ Sound alerts: ON")
    
    def create_frame(self):
        """Create demo frame with counters"""
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        frame[:] = (40, 40, 40)  # Dark background
        
        # Draw title
        cv2.putText(frame, "QUEUE MANAGEMENT ALERT DEMO", (150, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Draw counters
        for counter_id, pos in self.counter_positions.items():
            x, y, w, h = pos['x'], pos['y'], pos['width'], pos['height']
            
            # Scale down if too big
            if w > 600 or h > 400:
                scale = min(400/w, 300/h)
                x, y, w, h = int(x*scale), int(y*scale), int(w*scale), int(h*scale)
            
            # Draw counter rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 2)
            cv2.putText(frame, f"Counter {counter_id}", (x + 10, y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw vertical service line
            service_x = x + w // 3
            cv2.line(frame, (service_x, y), (service_x, y + h), (0, 255, 0), 3)
            cv2.putText(frame, "Service", (service_x + 5, y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, "Line", (service_x + 5, y + 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def add_customer(self):
        """Add a demo customer"""
        customer = {
            'id': len(self.customers) + 1,
            'service_start_time': time.time(),
            'queue_id': 1
        }
        self.customers.append(customer)
        print(f"✅ Added customer {customer['id']}")
    
    def draw_alerts(self, frame):
        """Draw service time alerts"""
        current_time = time.time()
        self.counter += 1
        
        alert_y = 70
        
        for customer in self.customers:
            service_time = current_time - customer['service_start_time']
            
            if service_time >= self.threshold:
                # Flash every 30 frames
                flash = (self.counter // 30) % 2 == 0
                
                if flash:
                    color = (0, 255, 255)  # Yellow
                    bg_color = (0, 0, 255)  # Red
                else:
                    color = (0, 0, 255)    # Red
                    bg_color = (0, 0, 0)   # Black
                
                # Draw alert box
                cv2.rectangle(frame, (50, alert_y), (750, alert_y + 70), bg_color, -1)
                cv2.rectangle(frame, (50, alert_y), (750, alert_y + 70), color, 4)
                
                # Alert text
                cv2.putText(frame, f"Customer {customer['id']}: {self.message}", 
                           (60, alert_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                cv2.putText(frame, f"Service Time: {service_time:.1f} seconds", 
                           (60, alert_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Play sound every 60 frames (about 2 seconds)
                if self.counter % 60 == 0:
                    try:
                        import winsound
                        winsound.Beep(1000, 300)
                        print(f"🚨 BEEP! Customer {customer['id']} - {service_time:.1f}s")
                    except:
                        print(f"🚨 ALERT! Customer {customer['id']} - {self.message} ({service_time:.1f}s)")
                
                alert_y += 80
        
        return frame
    
    def draw_info(self, frame):
        """Draw information and controls"""
        current_time = time.time()
        
        # Customer info
        y_pos = 400
        cv2.putText(frame, f"Active Customers: {len(self.customers)}", (50, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_pos += 30
        for customer in self.customers:
            service_time = current_time - customer['service_start_time']
            status = "⚠️ ALERT" if service_time >= self.threshold else "✅ OK"
            cv2.putText(frame, f"Customer {customer['id']}: {service_time:.1f}s {status}", 
                       (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 25
        
        # Controls
        cv2.putText(frame, "Controls:", (50, 520),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        cv2.putText(frame, "SPACE - Add Customer | R - Remove Customer | Q - Quit", (50, 550),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Alert Threshold: {self.threshold} seconds", (50, 580),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Run the standalone demo"""
        print("\nStarting demo...")
        print("Controls:")
        print("- SPACE: Add customer")
        print("- R: Remove oldest customer") 
        print("- Q: Quit")
        print("\nWatch for alerts after 5 seconds of service!")
        
        # Add initial customer
        self.add_customer()
        
        while True:
            # Create frame
            frame = self.create_frame()
            
            # Draw alerts
            frame = self.draw_alerts(frame)
            
            # Draw info
            frame = self.draw_info(frame)
            
            # Show frame
            cv2.imshow('Standalone Alert Demo', frame)
            
            # Handle keys
            key = cv2.waitKey(33) & 0xFF  # 30 FPS
            
            if key == ord('q'):
                break
            elif key == ord(' '):  # Space
                self.add_customer()
            elif key == ord('r'):
                if self.customers:
                    removed = self.customers.pop(0)
                    print(f"❌ Removed customer {removed['id']}")
        
        cv2.destroyAllWindows()
        print("Demo completed!")

if __name__ == "__main__":
    demo = StandaloneAlertDemo()
    demo.run()
