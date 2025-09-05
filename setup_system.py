"""
Complete Setup Script for Queue Management System
This script helps you set up counter positions for your specific video layout
"""

import os
import json
import sys

def show_banner():
    """Display welcome banner"""
    print("=" * 60)
    print("🏪 QUEUE MANAGEMENT SYSTEM SETUP")
    print("=" * 60)
    print("Welcome! Let's configure your counter layout.")
    print()

def check_video_file():
    """Check if user has a video file"""
    print("Do you have a video file to configure? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice == 'y':
        print("\nPlease enter the path to your video file:")
        video_path = input("Video path: ").strip().strip('"')
        
        if os.path.exists(video_path):
            return video_path
        else:
            print(f"❌ Video file not found: {video_path}")
            print("We'll use camera instead.")
            return None
    else:
        return None

def choose_configuration_method():
    """Let user choose configuration method"""
    print("\nHow would you like to configure your counter layout?")
    print("1. 🤖 Automatic Detection (AI detects counters)")
    print("2. ✋ Manual Configuration (Draw counter areas yourself)")
    print("3. 📋 Use Default Layout (4 counters in a row)")
    print()
    
    while True:
        choice = input("Enter your choice (1/2/3): ").strip()
        if choice in ['1', '2', '3']:
            return int(choice)
        print("Please enter 1, 2, or 3")

def run_auto_detection(video_path=None):
    """Run automatic counter detection"""
    print("\n🤖 Starting Automatic Counter Detection...")
    print("The AI will analyze your video and suggest counter positions.")
    
    try:
        if video_path:
            os.system(f'python auto_detect_layout.py --video "{video_path}"')
        else:
            os.system('python auto_detect_layout.py --camera 0')
        return True
    except Exception as e:
        print(f"❌ Error running auto detection: {e}")
        return False

def run_manual_configuration(video_path=None):
    """Run manual configuration"""
    print("\n✋ Starting Manual Configuration...")
    print("You'll be able to draw counter areas on your video.")
    
    try:
        if video_path:
            os.system(f'python configure_layout.py --video "{video_path}"')
        else:
            os.system('python configure_layout.py --camera 0')
        return True
    except Exception as e:
        print(f"❌ Error running manual configuration: {e}")
        return False

def create_default_config():
    """Create default counter configuration"""
    print("\n📋 Creating Default Configuration...")
    
    config = {
        "detection": {
            "confidence_threshold": 0.5,
            "nms_threshold": 0.4,
            "person_class_id": 0
        },
        "queue": {
            "max_customers_per_queue": 10,
            "service_time_threshold": 300,
            "queue_length_alert": 5,
            "optimal_wait_time": 180
        },
        "visual": {
            "line_thickness": 3,
            "colors": {
                "current_customer": [0, 255, 0],
                "waiting_line": [255, 0, 0],
                "queue_boundary": [0, 0, 255],
                "alert": [0, 165, 255]
            },
            "font_scale": 0.7,
            "font_thickness": 2
        },
        "performance": {
            "target_service_time": 120,
            "performance_threshold": 0.8,
            "alert_delay": 5,
            "break_time_tracking": True
        },
        "analytics": {
            "save_interval": 60,
            "report_generation": True,
            "data_retention_days": 30
        },
        "counters": {
            "total_counters": 4,
            "counter_positions": {
                "1": {"x": 100, "y": 100, "width": 200, "height": 300},
                "2": {"x": 350, "y": 100, "width": 200, "height": 300},
                "3": {"x": 600, "y": 100, "width": 200, "height": 300},
                "4": {"x": 850, "y": 100, "width": 200, "height": 300}
            },
            "express_lanes": [1, 2],
            "regular_lanes": [3, 4]
        }
    }
    
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print("✅ Default configuration saved to config.json")
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def test_system():
    """Test if the system works"""
    print("\n🧪 Testing System...")
    print("Running a quick test to make sure everything works...")
    
    try:
        # Run simple demo
        os.system('python simple_demo.py')
        return True
    except Exception as e:
        print(f"❌ Error testing system: {e}")
        return False

def show_final_instructions():
    """Show final instructions to user"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Your queue management system is now configured!")
    print()
    print("📖 How to run your system:")
    print("   • For full system:     python main.py")
    print("   • For simple demo:     python simple_demo.py")
    print("   • For alert demo:      python demo_with_alerts.py")
    print("   • For just detection:  python demo.py")
    print()
    print("🚨 Alert Features:")
    print("   • 5-second service time alerts")
    print("   • Visual flashing warnings") 
    print("   • Audio notifications (beep)")
    print("   • Message: 'You are late HurryUp!'")
    print()
    print("🔧 To reconfigure:")
    print("   • Auto detection:      python auto_detect_layout.py")
    print("   • Manual setup:        python configure_layout.py")
    print("   • This setup again:    python setup_system.py")
    print()
    print("📁 Your configuration is saved in: config.json")
    print()
    print("Happy queue monitoring! 🚀")

def main():
    """Main setup function"""
    show_banner()
    
    # Check for video file
    video_path = check_video_file()
    
    # Choose configuration method
    method = choose_configuration_method()
    
    success = False
    
    if method == 1:  # Automatic Detection
        success = run_auto_detection(video_path)
    elif method == 2:  # Manual Configuration
        success = run_manual_configuration(video_path)
    elif method == 3:  # Default Layout
        success = create_default_config()
    
    if success:
        print("\n✅ Configuration completed successfully!")
        
        # Ask if user wants to test
        print("\nWould you like to test the system now? (y/n): ", end="")
        test_choice = input().lower().strip()
        
        if test_choice == 'y':
            test_system()
        
        show_final_instructions()
    else:
        print("\n❌ Configuration failed. Please try again.")
        print("Make sure you have all required dependencies installed:")
        print("   pip install opencv-python numpy pandas matplotlib ultralytics")

if __name__ == "__main__":
    main()
