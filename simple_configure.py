"""
Simple Manual Counter Configuration Tool
Easy-to-use tool for setting up counter positions
"""

import cv2
import numpy as np
import json
import argparse

class SimpleCounterConfigurator:
    """Simple tool for manually configuring counter positions"""
    
    def __init__(self, video_path=None, camera_id=0):
        self.video_path = video_path
        self.camera_id = camera_id
        self.counters = []
        self.current_counter = None
        self.drawing = False
        self.start_point = None
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drawing counters"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing and self.start_point:
                self.current_counter = {
                    'x': min(self.start_point[0], x),
                    'y': min(self.start_point[1], y),
                    'width': abs(x - self.start_point[0]),
                    'height': abs(y - self.start_point[1])
                }
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing and self.current_counter:
                # Only add if counter is big enough
                if self.current_counter['width'] > 50 and self.current_counter['height'] > 50:
                    counter_id = len(self.counters) + 1
                    self.current_counter['id'] = counter_id
                    self.counters.append(self.current_counter.copy())
                    print(f"✓ Added Counter {counter_id}")
                
            self.drawing = False
            self.current_counter = None
            self.start_point = None
    
    def draw_interface(self, frame):
        """Draw the configuration interface"""
        overlay = frame.copy()
        
        # Draw existing counters
        for i, counter in enumerate(self.counters):
            x, y, w, h = counter['x'], counter['y'], counter['width'], counter['height']
            
            # Counter rectangle
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Vertical service line (customers line up behind this line)
            service_x = x + w // 3
            cv2.line(overlay, (service_x, y), (service_x, y + h), (255, 0, 0), 2)
            
            # Labels
            cv2.putText(overlay, f"Counter {counter['id']}", (x + 5, y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(overlay, "Service Line", (service_x + 5, y + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Draw current counter being drawn
        if self.current_counter:
            x, y, w, h = (self.current_counter['x'], self.current_counter['y'], 
                         self.current_counter['width'], self.current_counter['height'])
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 255), 2)
        
        # Instructions
        cv2.putText(overlay, "COUNTER SETUP - Click and drag to draw counter areas", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(overlay, f"Counters defined: {len(self.counters)}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(overlay, "Press 'S' to save, 'C' to clear, 'Q' to quit", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return overlay
    
    def save_configuration(self):
        """Save counter configuration to JSON file"""
        if not self.counters:
            print("❌ No counters defined!")
            return False
        
        try:
            # Load existing config or create new one
            config = {}
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
            except:
                # Default config structure
                config = {
                    "detection": {"confidence_threshold": 0.5, "nms_threshold": 0.4, "person_class_id": 0},
                    "queue": {"max_customers_per_queue": 10, "service_time_threshold": 300, "queue_length_alert": 5, "optimal_wait_time": 180},
                    "visual": {"line_thickness": 3, "colors": {"current_customer": [0, 255, 0], "waiting_line": [255, 0, 0], "queue_boundary": [0, 0, 255], "alert": [0, 165, 255]}, "font_scale": 0.7, "font_thickness": 2},
                    "performance": {"target_service_time": 120, "performance_threshold": 0.8, "alert_delay": 5, "break_time_tracking": True},
                    "analytics": {"save_interval": 60, "report_generation": True, "data_retention_days": 30}
                }
            
            # Update counter configuration
            if 'counters' not in config:
                config['counters'] = {}
            
            config['counters']['total_counters'] = len(self.counters)
            config['counters']['counter_positions'] = {}
            
            # Add counter positions
            for counter in self.counters:
                counter_id = str(counter['id'])
                config['counters']['counter_positions'][counter_id] = {
                    'x': counter['x'],
                    'y': counter['y'],
                    'width': counter['width'],
                    'height': counter['height']
                }
            
            # Set express/regular lanes
            total_counters = len(self.counters)
            express_count = max(1, total_counters // 2)
            config['counters']['express_lanes'] = list(range(1, express_count + 1))
            config['counters']['regular_lanes'] = list(range(express_count + 1, total_counters + 1))
            
            # Save to file
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"✅ Configuration saved with {total_counters} counters!")
            print("📁 Saved to: config.json")
            return True
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    
    def run(self):
        """Run the configuration tool"""
        print("Simple Counter Configuration Tool")
        print("=" * 40)
        
        # Initialize video capture
        if self.video_path:
            cap = cv2.VideoCapture(self.video_path)
            print(f"📹 Using video: {self.video_path}")
        else:
            cap = cv2.VideoCapture(self.camera_id)
            print(f"📷 Using camera: {self.camera_id}")
        
        if not cap.isOpened():
            print("❌ Error: Could not open video source")
            return False
        
        # Create window
        window_name = 'Simple Counter Setup'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        print("\n📖 Instructions:")
        print("   1. Click and drag to draw counter areas")
        print("   2. Press 'S' to save configuration")
        print("   3. Press 'C' to clear all counters")
        print("   4. Press 'Q' to quit")
        print()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    if self.video_path:
                        # Loop video
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        break
                
                # Draw interface
                display_frame = self.draw_interface(frame)
                
                # Show frame
                cv2.imshow(window_name, display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    if self.save_configuration():
                        print("Configuration saved successfully! You can now run your queue management system.")
                        break
                elif key == ord('c'):
                    self.counters = []
                    print("🗑️ Cleared all counters")
        
        except Exception as e:
            print(f"❌ Error during configuration: {e}")
            return False
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        return len(self.counters) > 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Simple Counter Configuration Tool')
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    
    args = parser.parse_args()
    
    configurator = SimpleCounterConfigurator(args.video, args.camera)
    success = configurator.run()
    
    if success:
        print("\n🎉 Setup complete!")
        print("You can now run: python main.py")
    else:
        print("\n❌ Setup incomplete")

if __name__ == "__main__":
    main()
