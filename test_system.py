"""
Test Script for Queue Management System
Tests individual components and overall system functionality
"""

import sys
import os
import time
import numpy as np

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from detector.person_detector import PersonDetector
        print("✓ PersonDetector imported successfully")
    except ImportError as e:
        print(f"✗ PersonDetector import failed: {e}")
        return False
    
    try:
        from queue_management.queue_manager import QueueManager
        print("✓ QueueManager imported successfully")
    except ImportError as e:
        print(f"✗ QueueManager import failed: {e}")
        return False
    
    try:
        from visual.interface_manager import InterfaceManager
        print("✓ InterfaceManager imported successfully")
    except ImportError as e:
        print(f"✗ InterfaceManager import failed: {e}")
        return False
    
    try:
        from analytics.performance_monitor import PerformanceMonitor
        print("✓ PerformanceMonitor imported successfully")
    except ImportError as e:
        print(f"✗ PerformanceMonitor import failed: {e}")
        return False
    
    try:
        from analytics.report_generator import ReportGenerator
        print("✓ ReportGenerator imported successfully")
    except ImportError as e:
        print(f"✗ ReportGenerator import failed: {e}")
        return False
    
    return True

def test_config_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required_sections = ['detection', 'queue', 'visual', 'counters', 'performance', 'analytics']
        for section in required_sections:
            if section in config:
                print(f"✓ Config section '{section}' found")
            else:
                print(f"✗ Config section '{section}' missing")
                return False
        
        return True
        
    except FileNotFoundError:
        print("✗ config.json file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config.json: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")
    
    dependencies = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn')
    ]
    
    missing_deps = []
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {package_name} is available")
        except ImportError:
            print(f"✗ {package_name} is missing")
            missing_deps.append(package_name)
    
    # Test YOLO specifically
    try:
        from ultralytics import YOLO
        print("✓ ultralytics (YOLO) is available")
    except ImportError:
        print("✗ ultralytics (YOLO) is missing")
        missing_deps.append('ultralytics')
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    return True

def test_detector():
    """Test person detector"""
    print("\nTesting PersonDetector...")
    
    try:
        from detector.person_detector import PersonDetector
        import json
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        detector = PersonDetector(config)
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test detection
        detections = detector.detect_persons(test_frame)
        print(f"✓ PersonDetector created and tested (found {len(detections)} detections)")
        
        # Test tracking
        tracked = detector.track_persons(detections)
        print(f"✓ Person tracking tested ({len(tracked)} tracked objects)")
        
        return True
        
    except Exception as e:
        print(f"✗ PersonDetector test failed: {e}")
        return False

def test_queue_manager():
    """Test queue manager"""
    print("\nTesting QueueManager...")
    
    try:
        from queue_management.queue_manager import QueueManager
        import json
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        queue_manager = QueueManager(config)
        
        # Test with dummy detections
        dummy_detections = [
            {'bbox': [150, 250, 40, 80], 'confidence': 0.8, 'center': [170, 290]},
            {'bbox': [400, 300, 40, 80], 'confidence': 0.9, 'center': [420, 340]}
        ]
        
        queue_data = queue_manager.update_queues(dummy_detections, (720, 1280))
        print(f"✓ QueueManager created and tested ({len(queue_data)} queues)")
        
        # Test metrics
        metrics = queue_manager.get_performance_metrics()
        print("✓ Performance metrics generated")
        
        return True
        
    except Exception as e:
        print(f"✗ QueueManager test failed: {e}")
        return False

def test_interface_manager():
    """Test interface manager"""
    print("\nTesting InterfaceManager...")
    
    try:
        from visual.interface_manager import InterfaceManager
        import json
        import cv2
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        interface_manager = InterfaceManager(config)
        
        # Test with dummy data
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        dummy_detections = []
        dummy_queue_data = {1: {'queue_length': 2, 'estimated_wait_time': 120}}
        dummy_metrics = {'total_customers_served': 10}
        
        result_frame = interface_manager.draw_interface(
            test_frame, dummy_detections, dummy_queue_data, dummy_metrics
        )
        
        print("✓ InterfaceManager created and tested")
        return True
        
    except Exception as e:
        print(f"✗ InterfaceManager test failed: {e}")
        return False

def test_performance_monitor():
    """Test performance monitor"""
    print("\nTesting PerformanceMonitor...")
    
    try:
        from analytics.performance_monitor import PerformanceMonitor
        import json
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        performance_monitor = PerformanceMonitor(config)
        
        # Test metrics update
        performance_monitor.update_metrics()
        
        # Test getting metrics
        metrics = performance_monitor.get_current_metrics()
        print("✓ PerformanceMonitor created and tested")
        
        # Test alerts
        alerts = performance_monitor.check_alerts()
        print(f"✓ Alert system tested ({len(alerts)} alerts)")
        
        return True
        
    except Exception as e:
        print(f"✗ PerformanceMonitor test failed: {e}")
        return False

def test_report_generator():
    """Test report generator"""
    print("\nTesting ReportGenerator...")
    
    try:
        from analytics.report_generator import ReportGenerator
        import json
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        report_generator = ReportGenerator(config)
        
        # Test manual report generation
        report_file = report_generator.generate_manual_report()
        print("✓ ReportGenerator created and tested")
        
        if report_file:
            print(f"✓ Manual report generated: {report_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ ReportGenerator test failed: {e}")
        return False

def test_main_system():
    """Test main system integration"""
    print("\nTesting main system integration...")
    
    try:
        from main import QueueManagementSystem
        
        # Create system instance
        system = QueueManagementSystem()
        print("✓ QueueManagementSystem created successfully")
        
        # Test configuration loading
        if system.config:
            print("✓ Configuration loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Main system test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("OpenCV Queue Management System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config_loading),
        ("Dependency Tests", test_dependencies),
        ("PersonDetector Tests", test_detector),
        ("QueueManager Tests", test_queue_manager),
        ("InterfaceManager Tests", test_interface_manager),
        ("PerformanceMonitor Tests", test_performance_monitor),
        ("ReportGenerator Tests", test_report_generator),
        ("Main System Tests", test_main_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ ALL TESTS PASSED - System is ready to run!")
        return True
    else:
        print("✗ Some tests failed - Check errors above")
        return False

def main():
    """Main test function"""
    success = run_all_tests()
    
    if success:
        print("\nTo run the system:")
        print("- For live camera: python main.py")
        print("- For demo mode: python demo.py")
        print("- For help: python main.py --help")
    else:
        print("\nPlease fix the issues above before running the system")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
