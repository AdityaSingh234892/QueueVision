"""
Test Main.py Integration
Test the main.py with integrated alert system
"""

import cv2
import numpy as np
import time
import sys
import os

def test_main_system():
    """Test the main system with integrated alerts"""
    print("🧪 Testing Main.py with Integrated Alert System")
    print("=" * 50)
    
    try:
        # Import main system
        sys.path.append(os.path.dirname(__file__))
        from main import QueueManagementSystem
        
        print("✅ Main system imported successfully")
        
        # Initialize system
        print("Initializing Queue Management System...")
        system = QueueManagementSystem()
        
        print("✅ System initialized with integrated alerts")
        print(f"   - Alert threshold: {system.alert_system.threshold} seconds")
        print(f"   - Alert message: '{system.alert_system.message}'")
        print(f"   - Sound enabled: {system.alert_system.sound_enabled}")
        
        # Test with camera
        print("\nTesting with camera/video...")
        print("Press 'q' to quit, 'a' to toggle alert sound, 'h' for help")
        
        system.run(camera_id=0)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your configuration and try again")

if __name__ == "__main__":
    test_main_system()
