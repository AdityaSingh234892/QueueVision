"""
Setup Script for OpenCV Queue Management System
Installs dependencies and sets up the environment
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def setup_environment():
    """Set up the Python environment with required packages"""
    print("OpenCV Queue Management System - Setup")
    print("=" * 40)
    
    # List of required packages
    packages = [
        "opencv-python",
        "numpy",
        "pandas", 
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "ultralytics",
        "Pillow"
    ]
    
    print("Installing required packages...")
    
    failed_packages = []
    
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✓ {package} installed successfully")
        else:
            print(f"✗ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\nFailed to install: {', '.join(failed_packages)}")
        print("Please install these manually:")
        for pkg in failed_packages:
            print(f"  pip install {pkg}")
        return False
    
    print("\n✓ All packages installed successfully!")
    return True

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = [
        "data",
        "data/reports", 
        "data/charts",
        "data/performance",
        "models"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def download_yolo_model():
    """Download YOLO model if not present"""
    print("\nDownloading YOLO model...")
    
    try:
        from ultralytics import YOLO
        
        # This will automatically download the model if not present
        model = YOLO('yolov8n.pt')
        print("✓ YOLO model ready")
        return True
        
    except Exception as e:
        print(f"✗ Failed to download YOLO model: {e}")
        return False

def verify_installation():
    """Verify the installation"""
    print("\nVerifying installation...")
    
    # Test imports
    test_imports = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("matplotlib", "Matplotlib"),
        ("seaborn", "Seaborn")
    ]
    
    all_good = True
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✓ {name} is working")
        except ImportError:
            print(f"✗ {name} import failed")
            all_good = False
    
    # Test YOLO
    try:
        from ultralytics import YOLO
        print("✓ YOLO is working")
    except ImportError:
        print("✗ YOLO import failed")
        all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("Setting up OpenCV Queue Management System...")
    
    # Install packages
    if not setup_environment():
        print("Setup failed during package installation")
        return 1
    
    # Create directories
    create_directories()
    
    # Download YOLO model
    if not download_yolo_model():
        print("Warning: YOLO model download failed. System will use HOG detector as fallback.")
    
    # Verify installation
    if verify_installation():
        print("\n" + "=" * 40)
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run tests: python test_system.py")
        print("2. Try demo: python demo.py")
        print("3. Run with camera: python main.py")
        print("4. Run with video: python main.py --video path/to/video.mp4")
        return 0
    else:
        print("\n" + "=" * 40)
        print("✗ Setup completed with errors")
        print("Some components may not work properly")
        return 1

if __name__ == "__main__":
    exit(main())
