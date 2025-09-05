#!/usr/bin/env python3
"""
Quick YOLO test
"""

print("Testing YOLO import...")

try:
    from ultralytics import YOLO
    print("✓ YOLO imported successfully")
    
    print("Testing YOLO model loading...")
    # This might download the model and take time
    model = YOLO('yolov8n.pt')
    print("✓ YOLO model loaded successfully")
    
except Exception as e:
    print(f"✗ YOLO error: {e}")
    print("YOLO not available - system will use HOG detector fallback")

print("Test complete!")
