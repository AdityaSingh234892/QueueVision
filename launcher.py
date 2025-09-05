"""
Queue Management System Launcher
Choose which version to run with integrated alerts
"""

import os
import sys

def show_menu():
    """Show available options"""
    print("🏪 QUEUE MANAGEMENT SYSTEM WITH ALERTS")
    print("=" * 50)
    print()
    print("Choose which version to run:")
    print()
    print("1. 🎯 Main System (Full Features + Alerts)")
    print("   - Complete queue management")
    print("   - Person detection")
    print("   - Performance analytics")
    print("   - 5-second alerts integrated")
    print("   Command: python main.py")
    print()
    print("2. 🎮 Simple Demo (Basic + Alerts)")
    print("   - Simple demonstration")
    print("   - Built-in alert system")
    print("   - Easy to use")
    print("   Command: python simple_demo.py")
    print()
    print("3. 🧪 Standalone Alert Demo")
    print("   - Pure alert system test")
    print("   - Interactive controls")
    print("   - No dependencies")
    print("   Command: python standalone_alert_demo.py")
    print()
    print("4. ⚡ Ultra Simple Alert Test")
    print("   - Quick alert verification")
    print("   - Minimal features")
    print("   Command: python ultra_simple_alert.py")
    print()
    print("🎮 Controls for Main System:")
    print("   Q - Quit")
    print("   A - Toggle alert sound ON/OFF")
    print("   S - Save report")
    print("   R - Reset counters")
    print("   H - Show help")
    print()
    print("🚨 Alert Features:")
    print("   ✅ 5-second service time threshold")
    print("   ✅ Visual flashing alerts (red/yellow)")
    print("   ✅ Audio beep notifications")
    print("   ✅ Message: 'You are late HurryUp!'")
    print("   ✅ Uses your counter layout from config.json")
    print()

def run_choice(choice):
    """Run the selected option"""
    if choice == '1':
        print("🎯 Starting Main System with Integrated Alerts...")
        print("Command: python main.py --camera 0")
        print("Press Ctrl+C to return to menu")
        os.system("python main.py --camera 0")
    elif choice == '2':
        print("🎮 Starting Simple Demo...")
        os.system("python simple_demo.py")
    elif choice == '3':
        print("🧪 Starting Standalone Alert Demo...")
        os.system("python standalone_alert_demo.py")
    elif choice == '4':
        print("⚡ Starting Ultra Simple Alert Test...")
        os.system("python ultra_simple_alert.py")
    else:
        print("❌ Invalid choice. Please select 1-4.")

def main():
    """Main launcher function"""
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-4, or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("👋 Goodbye!")
                break
            
            if choice in ['1', '2', '3', '4']:
                run_choice(choice)
                print("\n" + "="*50)
                input("Press Enter to return to menu...")
            else:
                print("❌ Invalid choice. Please select 1-4 or 'q' to quit.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
