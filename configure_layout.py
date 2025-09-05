"""
Counter Layout Configuration Tool
Allows you to define custom counter positions for your specific video/store layout
"""

import cv2
import numpy as np
import json
import os

class CounterLayoutConfigurator:
    """Interactive tool to configure counter positions"""
    
    def __init__(self, video_path=None, camera_id=0):
        self.video_path = video_path
        self.camera_id = camera_id
        self.counters = {}
        self.current_counter_id = 1
        self.drawing = False
        self.start_point = None
        self.temp_rect = None
        
        # Load existing config if available
        self.load_existing_config()
        
    def load_existing_config(self):
        """Load existing counter configuration"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                existing_positions = config.get('counters', {}).get('counter_positions', {})
                for counter_id, pos in existing_positions.items():
                    self.counters[int(counter_id)] = pos
                print(f"Loaded {len(self.counters)} existing counter positions")
        except:
            print("No existing configuration found, starting fresh")
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drawing counter areas"""
        frame = param
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.temp_rect = (self.start_point[0], self.start_point[1], 
                                x - self.start_point[0], y - self.start_point[1])
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                width = x - self.start_point[0]
                height = y - self.start_point[1]
                
                if abs(width) > 50 and abs(height) > 50:  # Minimum size
                    # Ensure positive width/height
                    x_pos = min(self.start_point[0], x)
                    y_pos = min(self.start_point[1], y)
                    width = abs(width)
                    height = abs(height)
                    
                    self.counters[self.current_counter_id] = {
                        "x": x_pos,
                        "y": y_pos, 
                        "width": width,
                        "height": height
                    }
                    
                    print(f"Added Counter {self.current_counter_id}: x={x_pos}, y={y_pos}, w={width}, h={height}")
                    self.current_counter_id += 1
                
                self.temp_rect = None
    
    def draw_interface(self, frame):
        """Draw the configuration interface"""
        # Create overlay
        overlay = frame.copy()
        
        # Draw existing counters
        for counter_id, pos in self.counters.items():
            x, y, w, h = pos["x"], pos["y"], pos["width"], pos["height"]
            
            # Draw counter rectangle
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw counter label
            cv2.putText(overlay, f"Counter {counter_id}", (x + 5, y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Draw vertical service line (customers line up behind this line)
            service_line_x = x + w // 3
            cv2.line(overlay, (service_line_x, y), (service_line_x, y + h), 
                    (255, 0, 0), 3)
            cv2.putText(overlay, "SERVICE LINE", (service_line_x + 5, y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Draw temporary rectangle being drawn
        if self.temp_rect:
            x, y, w, h = self.temp_rect
            if w > 0 and h > 0:
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 255, 0), 2)
        
        # Draw instructions
        instructions = [
            "COUNTER LAYOUT CONFIGURATOR",
            "",
            f"Next Counter: {self.current_counter_id}",
            "",
            "Instructions:",
            "1. Click and drag to define counter area",
            "2. Include checkout desk + queue area", 
            "3. Service line will be at top 25%",
            "4. Press 'S' to save configuration",
            "5. Press 'R' to reset all counters",
            "6. Press 'U' to undo last counter",
            "7. Press 'Q' to quit",
            "",
            f"Counters defined: {len(self.counters)}"
        ]
        
        y_offset = 30
        for instruction in instructions:
            if instruction == "COUNTER LAYOUT CONFIGURATOR":
                cv2.putText(overlay, instruction, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            elif instruction.startswith("Next Counter:"):
                cv2.putText(overlay, instruction, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            elif instruction.startswith("Counters defined:"):
                cv2.putText(overlay, instruction, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(overlay, instruction, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 25
        
        return overlay
    
    def save_configuration(self):
        """Save counter configuration to config.json"""
        try:
            # Load existing config
            config = {}
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
            
            # Update counter configuration
            if 'counters' not in config:
                config['counters'] = {}
            
            config['counters']['total_counters'] = len(self.counters)
            config['counters']['counter_positions'] = {}
            
            # Convert counter positions to string keys (JSON requirement)
            for counter_id, pos in self.counters.items():
                config['counters']['counter_positions'][str(counter_id)] = pos
            
            # Determine express lanes (first half of counters)
            total_counters = len(self.counters)
            express_lanes = list(range(1, (total_counters // 2) + 1))
            config['counters']['express_lanes'] = express_lanes
            config['counters']['regular_lanes'] = list(range((total_counters // 2) + 1, total_counters + 1))
            
            # Save configuration
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"\n✓ Configuration saved!")
            print(f"  - {total_counters} counters configured")
            print(f"  - Express lanes: {express_lanes}")
            print(f"  - Regular lanes: {config['counters']['regular_lanes']}")
            
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def run_configurator(self):
        """Run the interactive configuration tool"""
        print("Counter Layout Configurator")
        print("=" * 40)
        
        # Initialize video capture
        if self.video_path:
            cap = cv2.VideoCapture(self.video_path)
            print(f"Using video file: {self.video_path}")
        else:
            cap = cv2.VideoCapture(self.camera_id)
            print(f"Using camera: {self.camera_id}")
        
        if not cap.isOpened():
            print("Error: Could not open video source")
            return False
        
        # Create window and set mouse callback
        cv2.namedWindow('Counter Layout Configurator', cv2.WINDOW_NORMAL)
        
        frame_for_callback = None
        
        print("\nInstructions:")
        print("- Click and drag to define each counter area")
        print("- Include both checkout desk and waiting queue area")
        print("- The service line will automatically be placed at the top 25%")
        print("- Press 'S' to save, 'R' to reset, 'U' to undo, 'Q' to quit")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    if self.video_path:
                        # Loop video
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        print("Error reading from camera")
                        break
                
                frame_for_callback = frame.copy()
                cv2.setMouseCallback('Counter Layout Configurator', 
                                   self.mouse_callback, frame_for_callback)
                
                # Draw interface
                display_frame = self.draw_interface(frame)
                
                # Show frame
                cv2.imshow('Counter Layout Configurator', display_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    if self.save_configuration():
                        print("Configuration saved! You can now run the queue management system.")
                elif key == ord('r'):
                    self.counters.clear()
                    self.current_counter_id = 1
                    print("All counters reset")
                elif key == ord('u'):
                    if self.counters:
                        last_counter = max(self.counters.keys())
                        del self.counters[last_counter]
                        self.current_counter_id = max(self.counters.keys()) + 1 if self.counters else 1
                        print(f"Removed counter {last_counter}")
                
        except KeyboardInterrupt:
            print("\nConfiguration interrupted")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            if self.counters:
                print(f"\nFinal configuration: {len(self.counters)} counters defined")
                save_choice = input("Save configuration? (y/n): ")
                if save_choice.lower() == 'y':
                    self.save_configuration()
            
        return len(self.counters) > 0

def main():
    """Main function for counter layout configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configure counter layout for queue management system')
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    
    args = parser.parse_args()
    
    # Create configurator
    configurator = CounterLayoutConfigurator(
        video_path=args.video, 
        camera_id=args.camera
    )
    
    # Run configuration
    success = configurator.run_configurator()
    
    if success:
        print("\n" + "=" * 50)
        print("✓ Counter layout configured successfully!")
        print("\nNext steps:")
        print("1. Test with: python simple_demo.py")
        print("2. Run full system: python main.py")
        if args.video:
            print(f"3. Use your video: python main.py --video {args.video}")
    else:
        print("\nConfiguration cancelled or failed")

if __name__ == "__main__":
    main()
