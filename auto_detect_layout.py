"""
Automatic Counter Detection
Automatically detects counter positions from video using computer vision
"""

import cv2
import numpy as np
import json

class AutoCounterDetector:
    """Automatically detect counter positions from video"""
    
    def __init__(self):
        self.detected_counters = []
        
    def detect_counters_from_frame(self, frame):
        """Detect potential counter areas from a single frame"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        potential_counters = []
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size and aspect ratio
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # Counter criteria:
            # - Reasonable size (not too small/large)
            # - Vertical orientation (height > width for queue areas)
            # - Minimum area
            if (area > 5000 and area < frame.shape[0] * frame.shape[1] * 0.3 and
                aspect_ratio > 0.3 and aspect_ratio < 3.0 and
                w > 100 and h > 150):
                
                potential_counters.append({
                    'x': x, 'y': y, 'width': w, 'height': h,
                    'area': area, 'aspect_ratio': aspect_ratio
                })
        
        # Sort by area (largest first)
        potential_counters.sort(key=lambda c: c['area'], reverse=True)
        
        return potential_counters[:6]  # Return top 6 candidates
    
    def detect_horizontal_lines(self, frame):
        """Detect horizontal lines that might indicate checkout counters"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Use HoughLinesP to detect lines
        lines = cv2.HoughLinesP(
            cv2.Canny(gray, 50, 150),
            rho=1,
            theta=np.pi/180,
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )
        
        horizontal_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Check if line is roughly horizontal
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if angle < 15 or angle > 165:  # Nearly horizontal
                    length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    horizontal_lines.append({
                        'start': (x1, y1),
                        'end': (x2, y2),
                        'length': length,
                        'y_pos': (y1 + y2) // 2
                    })
        
        return horizontal_lines
    
    def suggest_counter_layout(self, frame):
        """Suggest counter layout based on frame analysis"""
        height, width = frame.shape[:2]
        
        # Method 1: Detect rectangular areas
        contour_counters = self.detect_counters_from_frame(frame)
        
        # Method 2: Detect horizontal lines (checkout desks)
        horizontal_lines = self.detect_horizontal_lines(frame)
        
        suggested_counters = []
        
        # Strategy 1: If we detect good rectangular areas
        if contour_counters:
            for i, counter in enumerate(contour_counters[:4]):  # Max 4 counters
                suggested_counters.append({
                    'id': i + 1,
                    'x': counter['x'],
                    'y': counter['y'],
                    'width': counter['width'],
                    'height': counter['height'],
                    'method': 'contour_detection',
                    'confidence': min(1.0, counter['area'] / 20000)
                })
        
        # Strategy 2: If no good contours, create default grid layout
        if not suggested_counters:
            # Create a grid layout based on frame size
            if width > height:  # Landscape orientation
                # Horizontal arrangement
                counter_width = width // 4
                counter_height = height // 2
                
                for i in range(4):
                    suggested_counters.append({
                        'id': i + 1,
                        'x': i * counter_width,
                        'y': height // 4,
                        'width': counter_width - 20,
                        'height': counter_height,
                        'method': 'grid_layout',
                        'confidence': 0.5
                    })
            else:  # Portrait orientation
                # Vertical arrangement
                counter_width = width // 2
                counter_height = height // 3
                
                for i in range(3):
                    for j in range(2):
                        if len(suggested_counters) < 4:
                            suggested_counters.append({
                                'id': len(suggested_counters) + 1,
                                'x': j * counter_width,
                                'y': i * counter_height + 50,
                                'width': counter_width - 20,
                                'height': counter_height - 30,
                                'method': 'grid_layout',
                                'confidence': 0.5
                            })
        
        return suggested_counters
    
    def visualize_suggestions(self, frame, suggestions):
        """Visualize suggested counter positions"""
        overlay = frame.copy()
        
        for counter in suggestions:
            x, y, w, h = counter['x'], counter['y'], counter['width'], counter['height']
            confidence = counter['confidence']
            
            # Choose color based on confidence
            if confidence > 0.8:
                color = (0, 255, 0)  # Green - high confidence
            elif confidence > 0.5:
                color = (0, 255, 255)  # Yellow - medium confidence
            else:
                color = (0, 0, 255)  # Red - low confidence
            
            # Draw counter rectangle
            cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
            
            # Draw vertical service line
            service_x = x + w // 3
            cv2.line(overlay, (service_x, y), (service_x, y + h), (255, 0, 0), 2)
            
            # Label
            label = f"Counter {counter['id']} ({confidence:.1f})"
            cv2.putText(overlay, label, (x + 5, y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Method info
            cv2.putText(overlay, counter['method'], (x + 5, y + h - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        return overlay

def run_auto_detection(video_path=None, camera_id=0):
    """Run automatic counter detection"""
    print("Automatic Counter Detection")
    print("=" * 30)
    
    # Initialize video capture
    if video_path:
        cap = cv2.VideoCapture(video_path)
        print(f"Analyzing video: {video_path}")
    else:
        cap = cv2.VideoCapture(camera_id)
        print(f"Analyzing camera: {camera_id}")
    
    if not cap.isOpened():
        print("Error: Could not open video source")
        return
    
    detector = AutoCounterDetector()
    
    print("\nInstructions:")
    print("- 'A' to accept current suggestions")
    print("- 'R' to refresh detection")
    print("- 'Q' to quit without saving")
    print("- 'M' to switch to manual configuration")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if video_path:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
            
            # Detect counter suggestions
            suggestions = detector.suggest_counter_layout(frame)
            
            # Visualize suggestions
            display_frame = detector.visualize_suggestions(frame, suggestions)
            
            # Add instructions
            cv2.putText(display_frame, "AUTO COUNTER DETECTION", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(display_frame, "A-Accept | R-Refresh | M-Manual | Q-Quit", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Auto Counter Detection', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('a'):
                # Accept suggestions and save
                if save_suggestions(suggestions):
                    print("✓ Auto-detected layout saved!")
                    break
            elif key == ord('r'):
                # Refresh detection (will happen automatically next frame)
                print("Refreshing detection...")
            elif key == ord('m'):
                # Switch to manual mode
                cap.release()
                cv2.destroyAllWindows()
                print("Switching to manual configuration...")
                from configure_layout import CounterLayoutConfigurator
                configurator = CounterLayoutConfigurator(video_path, camera_id)
                configurator.run_configurator()
                return
    
    except KeyboardInterrupt:
        print("\nDetection interrupted")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

def save_suggestions(suggestions):
    """Save suggested counter layout to config"""
    try:
        # Load existing config
        config = {}
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except:
            # Create default config structure
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
        
        config['counters']['total_counters'] = len(suggestions)
        config['counters']['counter_positions'] = {}
        
        # Convert suggestions to config format
        for suggestion in suggestions:
            counter_id = str(suggestion['id'])
            config['counters']['counter_positions'][counter_id] = {
                'x': suggestion['x'],
                'y': suggestion['y'],
                'width': suggestion['width'],
                'height': suggestion['height']
            }
        
        # Set express/regular lanes
        total_counters = len(suggestions)
        express_count = max(1, total_counters // 2)
        config['counters']['express_lanes'] = list(range(1, express_count + 1))
        config['counters']['regular_lanes'] = list(range(express_count + 1, total_counters + 1))
        
        # Save configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✓ Saved {total_counters} auto-detected counters")
        return True
        
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-detect counter layout')
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID')
    
    args = parser.parse_args()
    
    run_auto_detection(args.video, args.camera)
