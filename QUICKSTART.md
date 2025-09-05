# OpenCV Queue Management System - Quick Start Guide

## Overview
This system provides comprehensive retail queue monitoring with visual customer separation, time tracking, and performance analytics for stores like Walmart and DMart.

## Features
- **Real-time Customer Detection**: YOLO-based person detection and tracking
- **Visual Separation Lines**: Clear lines between current and waiting customers
- **Service Time Tracking**: Individual customer service time calculation
- **Performance Monitoring**: Cashier performance and efficiency analysis
- **Queue Analytics**: Wait time estimation and flow optimization
- **Automated Reporting**: Hourly, daily, and on-demand reports
- **Multi-counter Support**: Handle multiple checkout lanes simultaneously

## Quick Setup

### 1. Install Dependencies
```bash
python setup.py
```

### 2. Run Tests
```bash
python test_system.py
```

### 3. Try Demo Mode
```bash
python demo.py
```

### 4. Run with Camera
```bash
python main.py
```

### 5. Run with Video File
```bash
python main.py --video path/to/video.mp4
```

## System Controls

### During Operation:
- **Q** - Quit application
- **S** - Save manual report
- **R** - Reset all counters
- **H** - Show help

### Demo Mode Additional:
- **N** - Add new random customers

## Configuration

Edit `config.json` to customize:

```json
{
    "detection": {
        "confidence_threshold": 0.5,
        "model_type": "yolo"
    },
    "queue": {
        "max_customers_per_queue": 10,
        "service_time_threshold": 300
    },
    "counters": {
        "total_counters": 4,
        "express_lanes": [1, 2]
    }
}
```

## Counter Positions

The system supports 4 checkout counters by default:
- **Counters 1-2**: Express lanes
- **Counters 3-4**: Regular checkout lanes

Positions are defined in `config.json` and can be adjusted for your store layout.

## Visual Interface

### Real-time Display:
- **Green Lines**: Service area separation
- **Red Lines**: Queue boundaries
- **Customer Boxes**: Color-coded by status (current/waiting)
- **Performance Metrics**: Live statistics overlay
- **Alerts**: Real-time notifications

### Status Indicators:
- **Green Circle**: Good queue performance
- **Yellow Circle**: Warning (longer queues)
- **Red Circle**: Critical (very long queues)

## Performance Monitoring

### Metrics Tracked:
- Individual customer service times
- Queue lengths and wait times
- Cashier performance scores
- System efficiency ratings
- Peak hour analysis

### Alerts Generated:
- Long service times
- Queue bottlenecks
- Cashier performance issues
- System inefficiencies

## Reports and Analytics

### Automatic Reports:
- **Hourly**: Performance summaries
- **Daily**: Comprehensive analysis
- **Final**: Session summary on shutdown

### Manual Reports:
- Press 'S' during operation
- Saved to `data/reports/` directory

### Charts and Visualizations:
- Performance trends
- Queue analysis
- Service time distributions
- Efficiency dashboards

## Data Storage

### Directory Structure:
```
data/
├── reports/          # Generated reports
├── charts/           # Performance charts
├── performance/      # Performance data
└── queue_data_*.json # Raw queue data
```

### Data Retention:
- Default: 30 days
- Configurable in `config.json`

## Troubleshooting

### Common Issues:

1. **Camera not detected**:
   - Check camera connection
   - Try different camera ID: `python main.py --camera 1`

2. **YOLO model download fails**:
   - System automatically falls back to HOG detector
   - Manually download: `pip install ultralytics`

3. **Performance issues**:
   - Reduce frame resolution in camera settings
   - Lower detection confidence threshold

4. **Import errors**:
   - Run `python setup.py` again
   - Check `python test_system.py` output

### Getting Help:
- Run `python main.py --help` for command line options
- Check console output for error messages
- Review test results: `python test_system.py`

## Advanced Usage

### Custom Counter Layouts:
Modify `counter_positions` in `config.json`:
```json
"counter_positions": {
    "1": {"x": 100, "y": 200, "width": 200, "height": 400}
}
```

### Performance Tuning:
- Adjust detection confidence thresholds
- Modify service time targets
- Configure alert sensitivity

### Integration:
- Export data as JSON for external systems
- Generate CSV reports for spreadsheet analysis
- Customize report formats

## System Requirements

### Minimum:
- Python 3.7+
- 4GB RAM
- Webcam or video input
- Windows/Linux/Mac

### Recommended:
- Python 3.9+
- 8GB RAM
- GPU support for faster detection
- Multiple cameras for large stores

## Security and Privacy

- No video data is stored permanently
- Only analytics and metrics are saved
- Customer identification is temporary
- All data processing is local

## Support

For issues or questions:
1. Check this quick start guide
2. Run system tests
3. Review console output
4. Check configuration settings

The system is designed to be robust and will continue operating even if some components fail, using fallback methods when necessary.
