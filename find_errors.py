#!/usr/bin/env python3
"""
Simple error detection script
"""

def test_imports():
    errors = []
    
    # Test basic imports
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except Exception as e:
        errors.append(f"OpenCV error: {e}")
        print(f"✗ OpenCV error: {e}")
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except Exception as e:
        errors.append(f"NumPy error: {e}")
        print(f"✗ NumPy error: {e}")
    
    try:
        from ultralytics import YOLO
        print("✓ YOLO imported successfully")
    except Exception as e:
        errors.append(f"YOLO error: {e}")
        print(f"✗ YOLO error: {e}")
    
    # Test our modules
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from detector.person_detector import PersonDetector
        print("✓ PersonDetector imported successfully")
    except Exception as e:
        errors.append(f"PersonDetector error: {e}")
        print(f"✗ PersonDetector error: {e}")
    
    try:
        from queue_management.queue_manager import QueueManager
        print("✓ QueueManager imported successfully")
    except Exception as e:
        errors.append(f"QueueManager error: {e}")
        print(f"✗ QueueManager error: {e}")
    
    try:
        from visual.interface_manager import InterfaceManager
        print("✓ InterfaceManager imported successfully")
    except Exception as e:
        errors.append(f"InterfaceManager error: {e}")
        print(f"✗ InterfaceManager error: {e}")
    
    # Test main system
    try:
        from main import QueueManagementSystem
        print("✓ Main system imported successfully")
    except Exception as e:
        errors.append(f"Main system error: {e}")
        print(f"✗ Main system error: {e}")
    
    return errors

def test_demo():
    try:
        from demo import DemoQueueSystem
        print("✓ Demo system imported successfully")
        return True
    except Exception as e:
        print(f"✗ Demo system error: {e}")
        return False

if __name__ == "__main__":
    print("Error Detection Script")
    print("=" * 30)
    
    print("\nTesting imports...")
    errors = test_imports()
    
    print("\nTesting demo system...")
    demo_ok = test_demo()
    
    print("\n" + "=" * 30)
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ All imports successful!")
    
    if not demo_ok:
        print("Demo system has issues")
    else:
        print("✓ Demo system ready!")
