"""
Diagnostic Script for Queue Management System
Checks system health and provides troubleshooting information
"""

import sys
import os
import platform
import subprocess
import json

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

def check_python_version():
    """Check Python version"""
    print_section("PYTHON VERSION")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.7+ required")
        return False

def check_system_info():
    """Check system information"""
    print_section("SYSTEM INFORMATION")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"Total RAM: {memory.total // (1024**3)} GB")
        print(f"Available RAM: {memory.available // (1024**3)} GB")
    except ImportError:
        print("Memory info not available (psutil not installed)")

def check_dependencies():
    """Check required dependencies"""
    print_section("DEPENDENCY CHECK")
    
    required_packages = [
        ('cv2', 'opencv-python', 'OpenCV for computer vision'),
        ('numpy', 'numpy', 'NumPy for numerical operations'),
        ('pandas', 'pandas', 'Pandas for data handling'),
        ('matplotlib', 'matplotlib', 'Matplotlib for plotting'),
        ('seaborn', 'seaborn', 'Seaborn for advanced plotting'),
        ('ultralytics', 'ultralytics', 'YOLO for object detection')
    ]
    
    missing = []
    working = []
    
    for module, package, description in required_packages:
        try:
            __import__(module)
            print(f"✓ {package} - {description}")
            working.append(package)
        except ImportError:
            print(f"✗ {package} - {description} [MISSING]")
            missing.append(package)
    
    print(f"\nSummary: {len(working)}/{len(required_packages)} dependencies available")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
    
    return len(missing) == 0

def check_camera_access():
    """Check camera access"""
    print_section("CAMERA ACCESS")
    
    try:
        import cv2
        
        # Try to open default camera
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                print(f"✓ Camera 0 accessible")
                print(f"  Resolution: {width}x{height}")
                print(f"  Frame captured successfully")
            else:
                print("✗ Camera 0 opened but no frame captured")
            
            cap.release()
        else:
            print("✗ Cannot open camera 0")
            print("  - Check camera connection")
            print("  - Try a different camera ID")
            print("  - Check camera permissions")
        
        # Check for additional cameras
        for cam_id in range(1, 4):
            cap = cv2.VideoCapture(cam_id)
            if cap.isOpened():
                print(f"✓ Camera {cam_id} also available")
                cap.release()
    
    except ImportError:
        print("✗ OpenCV not available - cannot test camera")

def check_file_structure():
    """Check project file structure"""
    print_section("PROJECT STRUCTURE")
    
    required_files = [
        'config.json',
        'main.py',
        'demo.py',
        'requirements.txt',
        'README.md'
    ]
    
    required_dirs = [
        'src',
        'src/detector',
        'src/queue', 
        'src/visual',
        'src/analytics'
    ]
    
    print("Files:")
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file} ({size} bytes)")
        else:
            print(f"✗ {file} [MISSING]")
    
    print("\nDirectories:")
    for directory in required_dirs:
        if os.path.isdir(directory):
            files = len(os.listdir(directory))
            print(f"✓ {directory} ({files} files)")
        else:
            print(f"✗ {directory} [MISSING]")

def check_configuration():
    """Check configuration file"""
    print_section("CONFIGURATION")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("✓ config.json is valid JSON")
        
        required_sections = ['detection', 'queue', 'visual', 'counters', 'performance', 'analytics']
        
        for section in required_sections:
            if section in config:
                print(f"✓ Section '{section}' present")
            else:
                print(f"✗ Section '{section}' missing")
        
        # Check counter configuration
        if 'counters' in config:
            total_counters = config['counters'].get('total_counters', 0)
            positions = config['counters'].get('counter_positions', {})
            print(f"  - {total_counters} counters configured")
            print(f"  - {len(positions)} counter positions defined")
    
    except FileNotFoundError:
        print("✗ config.json not found")
    except json.JSONDecodeError as e:
        print(f"✗ config.json is invalid: {e}")

def check_data_directories():
    """Check data directories"""
    print_section("DATA DIRECTORIES")
    
    data_dirs = [
        'data',
        'data/reports',
        'data/charts', 
        'data/performance'
    ]
    
    for directory in data_dirs:
        if os.path.isdir(directory):
            files = os.listdir(directory)
            print(f"✓ {directory} ({len(files)} files)")
        else:
            print(f"✗ {directory} [MISSING]")
            print(f"  Create with: mkdir {directory}")

def check_yolo_model():
    """Check YOLO model availability"""
    print_section("YOLO MODEL")
    
    try:
        from ultralytics import YOLO
        
        print("Attempting to load YOLO model...")
        model = YOLO('yolov8n.pt')
        print("✓ YOLO model loaded successfully")
        print(f"  Model path: {model.ckpt_path}")
        
        # Test inference on dummy image
        import numpy as np
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        results = model(dummy_image, verbose=False)
        print("✓ YOLO inference test passed")
        
    except ImportError:
        print("✗ ultralytics not available")
    except Exception as e:
        print(f"✗ YOLO model error: {e}")

def test_basic_functionality():
    """Test basic system functionality"""
    print_section("BASIC FUNCTIONALITY TEST")
    
    try:
        # Test imports
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from detector.person_detector import PersonDetector
        from queue_management.queue_manager import QueueManager
        
        print("✓ Core modules import successfully")
        
        # Test config loading
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Test detector creation
        detector = PersonDetector(config)
        print("✓ PersonDetector created")
        
        # Test queue manager creation
        queue_manager = QueueManager(config)
        print("✓ QueueManager created")
        
        print("✓ Basic functionality test passed")
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")

def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report"""
    print_section("DIAGNOSTIC SUMMARY")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies), 
        ("File Structure", lambda: (check_file_structure(), True)[1]),
        ("Configuration", lambda: (check_configuration(), True)[1])
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
        except Exception as e:
            print(f"Error in {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"\nDiagnostic Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ System appears to be ready!")
        print("\nRecommended next steps:")
        print("1. python demo.py - Try demo mode")
        print("2. python main.py - Run with camera")
    else:
        print("✗ Some issues found. Please address them before running.")
        
        failed_checks = [name for name, result in results.items() if not result]
        print(f"\nFailed checks: {', '.join(failed_checks)}")

def main():
    """Main diagnostic function"""
    print("OpenCV Queue Management System - Diagnostic Tool")
    print(f"Running diagnostics from: {os.getcwd()}")
    
    # Run all checks
    check_python_version()
    check_system_info()
    check_dependencies()
    check_camera_access()
    check_file_structure()
    check_configuration()
    check_data_directories()
    check_yolo_model()
    test_basic_functionality()
    
    # Generate summary
    generate_diagnostic_report()
    
    print(f"\n{'='*50}")
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()
