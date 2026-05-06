# Real-Time Analog Pressure Gauge Reader

An OpenCV-based system for real-time detection and conversion of analog pressure gauges to digital pressure values. Designed to integrate with the FireDesk pump room dashboard.

## Features

✅ Real-time webcam video capture  
✅ Circular gauge detection using Hough Circle Transform  
✅ Needle detection using Hough Line Transform  
✅ Angle-to-pressure conversion  
✅ JSON-based calibration system  
✅ FPS display and optimization  
✅ Keyboard controls (q=quit, c=calibrate)  
✅ Support for PSI, bar, kPa gauges  

## Installation

```bash
cd /home/h4ck3r/Projects/FireDesk/gauge_reader
pip install -r requirements.txt
```

## Quick Start

```bash
python src/main.py --calibration calibrations/default_psi.json
```

## Keyboard Controls

- **q**: Quit application
- **c**: Enter calibration mode
- **s**: Save current frame
- **r**: Reset to normal mode

## Calibration

Each gauge requires a calibration JSON file with these parameters:

```json
{
  "gauge_name": "Pump Pressure PSI",
  "unit": "PSI",
  "min_angle": 45,
  "max_angle": 315,
  "min_pressure": 0,
  "max_pressure": 100,
  "hough_circles_param1": 100,
  "hough_circles_param2": 30,
  "hough_circles_minRadius": 50,
  "hough_circles_maxRadius": 300
}
```

### Pressure Formula

```
Pressure = ((angle - min_angle) / (max_angle - min_angle)) * (max_pressure - min_pressure) + min_pressure
```

## File Structure

```
gauge_reader/
├── src/
│   ├── main.py                 # Entry point with real-time processing
│   ├── gauge_detector.py       # Core gauge and needle detection
│   ├── calibrator.py           # Interactive calibration system
│   ├── config_manager.py       # JSON calibration file manager
│   └── utils.py                # Helper functions
├── calibrations/
│   ├── default_psi.json        # PSI gauge calibration
│   ├── default_bar.json        # bar gauge calibration
│   └── default_kpa.json        # kPa gauge calibration
├── test_images/                # Test gauge images
├── output/                     # Output frames and logs
└── requirements.txt            # Python dependencies
```

## Performance Tips

1. **Adjust Gaussian Blur**: Increase kernel size (15, 15) for noisy video
2. **Adjust Canny Threshold**: Lower threshold for faint needles
3. **Hough Circles Parameters**:
   - `param1`: Canny threshold (default: 100)
   - `param2`: Accumulator threshold (default: 30)
   - Decrease `param2` to detect more circles
4. **Hough Lines Parameters**:
   - Increase `minLineLength` for stable needle detection
   - Decrease `maxLineGap` for connected lines

## Integration with FireDesk

The pressure values can be sent to the FireDesk dashboard via:
1. UDP/TCP socket connection
2. JSON file updates
3. REST API endpoints
4. Direct Python imports for component integration

See `examples/firedesk_integration.py` for integration patterns.
