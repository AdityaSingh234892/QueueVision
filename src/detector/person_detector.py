"""
Person Detection Module
Handles customer detection and tracking using OpenCV and YOLO
"""

import cv2
import numpy as np
import platform
import time
from collections import defaultdict, deque

class PersonDetector:
    """Person detection and tracking class"""
    
    def __init__(self, config):
        """Initialize the person detector"""
        self.config = config["detection"]
        self.confidence_threshold = self.config.get("confidence_threshold", 0.5)
        self.nms_threshold = self.config.get("nms_threshold", 0.4)
        self.person_class_id = self.config.get("person_class_id", 0)
        
        # Initialize detection model with Windows-friendly approach
        self.model = None
        self.hog = None
        
        # On Windows, default to HOG to avoid YOLO download delays
        if platform.system() == "Windows":
            print("Windows detected - using HOG detector for reliability")
            self.use_hog_detector()
        else:
            # Try YOLO first on other platforms
            try:
                print("Attempting to load YOLO model...")
                from ultralytics import YOLO
                self.model = YOLO('yolov8n.pt')
                print("✓ YOLO model loaded successfully")
            except Exception as e:
                print(f"YOLO unavailable ({e}), using HOG detector")
                self.use_hog_detector()
    
    def use_hog_detector(self):
        """Initialize HOG detector"""
        self.model = None
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        print("✓ HOG detector initialized")
        
        # Tracking variables
        self.tracked_persons = {}
        self.next_id = 1
        self.max_disappeared = 30  # frames
        self.max_distance = 100    # pixels
        
        # Performance tracking
        self.detection_times = deque(maxlen=100)
    
    def detect_persons_yolo(self, frame):
        """Detect persons using YOLO"""
        start_time = time.time()
        
        try:
            # Run YOLO detection
            results = self.model(frame, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Check if detection is a person and meets confidence threshold
                        if (int(box.cls) == self.person_class_id and 
                            float(box.conf) >= self.confidence_threshold):
                            
                            # Extract bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = float(box.conf)
                            
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2-x1), int(y2-y1)],
                                'confidence': confidence,
                                'center': [int((x1+x2)/2), int((y1+y2)/2)]
                            })
            
            detection_time = time.time() - start_time
            self.detection_times.append(detection_time)
            
            return detections
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return []
    
    def detect_persons_hog(self, frame):
        """Detect persons using HOG descriptor (fallback)"""
        start_time = time.time()
        
        try:
            # Convert to grayscale for HOG
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect persons
            boxes, weights = self.hog.detectMultiScale(
                gray, 
                winStride=(8, 8),
                padding=(32, 32),
                scale=1.05
            )
            
            detections = []
            for i, (x, y, w, h) in enumerate(boxes):
                if weights[i] >= self.confidence_threshold:
                    detections.append({
                        'bbox': [x, y, w, h],
                        'confidence': weights[i],
                        'center': [x + w//2, y + h//2]
                    })
            
            detection_time = time.time() - start_time
            self.detection_times.append(detection_time)
            
            return detections
            
        except Exception as e:
            print(f"HOG detection error: {e}")
            return []
    
    def detect_persons(self, frame):
        """Main detection method"""
        if self.model is not None:
            return self.detect_persons_yolo(frame)
        else:
            return self.detect_persons_hog(frame)
    
    def track_persons(self, detections):
        """Track persons across frames with unique IDs"""
        current_centers = [det['center'] for det in detections]
        
        # Update existing tracks
        updated_tracks = set()
        for track_id, track_data in list(self.tracked_persons.items()):
            best_match_idx = None
            min_distance = float('inf')
            
            # Find closest detection to this track
            for i, center in enumerate(current_centers):
                distance = np.sqrt((center[0] - track_data['center'][0])**2 + 
                                 (center[1] - track_data['center'][1])**2)
                
                if distance < min_distance and distance < self.max_distance:
                    min_distance = distance
                    best_match_idx = i
            
            if best_match_idx is not None:
                # Update track
                self.tracked_persons[track_id].update({
                    'center': current_centers[best_match_idx],
                    'bbox': detections[best_match_idx]['bbox'],
                    'confidence': detections[best_match_idx]['confidence'],
                    'disappeared': 0,
                    'last_seen': time.time()
                })
                updated_tracks.add(best_match_idx)
            else:
                # Track not matched, increment disappeared counter
                self.tracked_persons[track_id]['disappeared'] += 1
        
        # Remove tracks that have disappeared for too long
        to_remove = []
        for track_id, track_data in self.tracked_persons.items():
            if track_data['disappeared'] > self.max_disappeared:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracked_persons[track_id]
        
        # Add new tracks for unmatched detections
        for i, detection in enumerate(detections):
            if i not in updated_tracks:
                self.tracked_persons[self.next_id] = {
                    'center': detection['center'],
                    'bbox': detection['bbox'],
                    'confidence': detection['confidence'],
                    'disappeared': 0,
                    'first_seen': time.time(),
                    'last_seen': time.time()
                }
                self.next_id += 1
        
        return self.tracked_persons
    
    def get_detection_stats(self):
        """Get detection performance statistics"""
        if not self.detection_times:
            return {
                'avg_detection_time': 0,
                'fps': 0,
                'total_detections': 0
            }
        
        avg_time = sum(self.detection_times) / len(self.detection_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        return {
            'avg_detection_time': avg_time,
            'fps': fps,
            'total_detections': len(self.tracked_persons)
        }
    
    def reset_tracking(self):
        """Reset all tracking data"""
        self.tracked_persons.clear()
        self.next_id = 1
        self.detection_times.clear()
    
    def get_persons_in_area(self, area_coords):
        """Get persons within a specific area"""
        x, y, w, h = area_coords
        persons_in_area = []
        
        for track_id, track_data in self.tracked_persons.items():
            center_x, center_y = track_data['center']
            
            if (x <= center_x <= x + w and y <= center_y <= y + h):
                persons_in_area.append({
                    'id': track_id,
                    'center': track_data['center'],
                    'bbox': track_data['bbox'],
                    'confidence': track_data['confidence'],
                    'first_seen': track_data['first_seen'],
                    'last_seen': track_data['last_seen']
                })
        
        return persons_in_area
