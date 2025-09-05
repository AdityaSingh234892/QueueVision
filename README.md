# OpenCV Queue Management System

A comprehensive Python application using OpenCV that monitors retail store queues, provides visual customer separation, and tracks service times for optimization.

## Features

- **Customer Detection**: Real-time person detection and tracking in checkout queues
- **Visual Separation**: Clear line separation between current and waiting customers
- **Time Tracking**: Individual customer service time calculation
- **Queue Analytics**: Position tracking and wait time estimation
- **Performance Monitoring**: Cashier performance and counter efficiency analysis
- **Billing Optimization**: Queue distribution and staffing recommendations
- **Real-time Interface**: Live video feed with overlay graphics and alerts

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the main application:
```bash
python main.py
```

## Project Structure

- `main.py` - Main application entry point
- `src/` - Source code modules
  - `detector/` - Person detection and tracking
  - `queue/` - Queue management and analytics
  - `visual/` - Visual interface and line drawing
  - `analytics/` - Performance monitoring and reporting
  - `config/` - Configuration settings
- `data/` - Data storage and exports
- `models/` - Pre-trained models for detection

## Usage

The system supports multiple checkout counters and provides real-time monitoring with visual feedback for queue optimization in retail environments like Walmart and DMart.
