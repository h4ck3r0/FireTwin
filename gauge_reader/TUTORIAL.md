# Step-by-Step Tutorial: Real-Time Analog Gauge Reading

## Overview

This tutorial guides you through setting up and using the real-time analog gauge reader integrated into your FireDesk project.

## Part 1: Installation & Setup

### Step 1: Install Python Dependencies

```bash
cd /home/h4ck3r/Projects/FireDesk/gauge_reader
pip install -r requirements.txt
```

This installs:
- `opencv-python`: Computer vision library
- `numpy`: Numerical computing
- `json5`: Enhanced JSON support

### Step 2: Create Default Calibrations

The system automatically creates default calibration files on first run:

```bash
python src/main.py --list-calibrations
```

You should see:
```
Available calibrations:
  - default_psi.json
  - default_bar.json
  - default_kpa.json
```

## Part 2: Calibrating a Gauge

### Option A: Quick Start with Default Calibration

```bash
python src/main.py --calibration calibrations/default_psi.json
```

This uses pre-configured settings for a 0-100 PSI gauge.

### Option B: Interactive Calibration Wizard

For precise calibration of your specific gauge:

```bash
python src/main.py --calibrate
```

**Calibration Steps:**
1. Enter gauge name: `"Pump Room Pressure"`
2. Enter unit: `PSI`
3. Enter min pressure: `0`
4. Enter max pressure: `100`
5. Point needle at minimum pressure marking → Press ENTER
6. Point needle at maximum pressure marking → Press ENTER
7. Configuration saved to `calibrations/`

## Part 3: Running Real-Time Detection

### Basic Operation

```bash
python src/main.py --calibration calibrations/default_psi.json
```

**What You'll See:**
- Live video feed with gauge circle (cyan)
- Detected needle (red line)
- Current angle reading
- Current pressure reading
- FPS and detection rate

### Keyboard Controls

- **`q`** - Quit application
- **`c`** - Enter calibration mode
- **`SPACE`** - Pause/Resume video
- **`s`** - Save current frame
- **`r`** - Reset to normal mode
- **`ENTER`** (in calibration mode) - Confirm step

## Part 4: Understanding the Display

```
FPS: 28.5
Detection: 95.3%
✓ DETECTING
```

**Interpretation:**
- **FPS**: Frames per second (higher = better, 30+ is real-time)
- **Detection**: Percentage of frames where gauge was detected
- **Status**: Green checkmark = detection successful, red X = no detection

### On-Screen Readings

```
Angle: 127.5°
Pressure: 65.3 PSI
```

- **Angle**: Needle position in degrees (0-360)
- **Pressure**: Converted pressure value using calibration

## Part 5: Tuning for Your Environment

### Problem: Circle Not Detected

Edit calibration file and decrease `param2`:

```json
{
  "hough_circles_param2": 20
}
```

Run again: `python src/main.py --calibration calibrations/default_psi.json`

### Problem: Needle Not Detected

Decrease Canny thresholds in calibration:

```json
{
  "canny_threshold1": 30,
  "canny_threshold2": 100
}
```

### Problem: Shaky Readings

Increase needle detection stability:

```json
{
  "hough_lines_minLineLength": 80,
  "canny_threshold2": 200
}
```

For detailed tuning guide, see [TUNING_GUIDE.md](TUNING_GUIDE.md)

## Part 6: Working with Different Gauge Types

### For PSI Gauges (0-100)
```bash
python src/main.py --calibration calibrations/default_psi.json
```

### For bar Gauges (0-10)
```bash
python src/main.py --calibration calibrations/default_bar.json
```

### For kPa Gauges (0-1000)
```bash
python src/main.py --calibration calibrations/default_kpa.json
```

### For Custom Gauges
Create calibration JSON in `calibrations/`:

```json
{
  "gauge_name": "Custom Pump Gauge",
  "unit": "PSI",
  "min_angle": 45,
  "max_angle": 315,
  "min_pressure": 0,
  "max_pressure": 150,
  "hough_circles_param1": 100,
  "hough_circles_param2": 30,
  "hough_circles_minRadius": 50,
  "hough_circles_maxRadius": 300,
  "canny_threshold1": 50,
  "canny_threshold2": 150,
  "gaussian_kernel": [15, 15],
  "hough_lines_minLineLength": 50,
  "hough_lines_maxLineGap": 10
}
```

## Part 7: Integration with FireDesk

### Sending Gauge Readings to FireDesk Dashboard

Run the integration module:

```bash
python firedesk_integration.py
```

This:
1. Reads gauge pressure in real-time
2. Sends readings to FireDesk dashboard via UDP
3. Updates `gauge_status.json` file
4. Logs readings to console

### Updating Your FireDesk Dashboard

In your React component, read from `gauge_status.json`:

```javascript
import { useEffect, useState } from 'react';

export function GaugeReading() {
  const [pressure, setPressure] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('/gauge_status.json');
      const data = await response.json();
      setPressure(data['Pump Room Pressure']?.pressure || 0);
    }, 100);
    
    return () => clearInterval(interval);
  }, []);
  
  return <div>Live Pressure: {pressure.toFixed(1)} PSI</div>;
}
```

## Part 8: Troubleshooting

### Issue: "Cannot open video capture device"
- Check webcam connection
- Try: `python -c "import cv2; print(cv2.__version__)"`
- On Linux, may need: `sudo apt install libsm6 libxext6`

### Issue: Very Low FPS (< 5)
1. Reduce frame resolution in camera settings
2. Increase Gaussian blur: `"gaussian_kernel": [21, 21]`
3. Close other applications using GPU

### Issue: Detection Rate Very Low (< 50%)
1. Improve lighting (use LED lamp)
2. Clean camera lens
3. Decrease Canny thresholds
4. Run calibration again with better positioning

### Issue: Pressure Values Jumping Around
1. Increase smoothing in `src/main.py`
2. Find line: `alpha=0.7`
3. Change to: `alpha=0.9` (more smoothing)
4. Or re-calibrate more carefully

## Part 9: Performance Tips

### For Maximum Speed (Real-Time Video)
1. Use smaller Gaussian kernel: `[11, 11]`
2. Increase HoughCircles param2: `50-100`
3. Increase minLineLength: `80-100`

### For Maximum Accuracy
1. Use larger Gaussian kernel: `[21, 21]`
2. Decrease param2: `10-20`
3. Decrease Canny thresholds
4. Use higher resolution input

### Measuring Actual Performance

The application shows:
- **FPS**: Real frames per second
- **Detection Rate**: Percentage of successful detections

Target: 25-30 FPS with >90% detection rate

## Part 10: Advanced Usage

### Using as Python Module

```python
from gauge_reader.src.gauge_detector import GaugeDetector
from gauge_reader.src.config_manager import CalibrationConfig
import cv2

# Load calibration
config = CalibrationConfig('gauge_reader/calibrations/default_psi.json')

# Create detector
detector = GaugeDetector(config)

# Process frame
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
results = detector.process_frame(frame)

print(f"Pressure: {results['pressure']} {results['pressure_unit']}")
```

### Batch Processing Images

```bash
# Process all images in a directory
python -c "
from gauge_reader.src.gauge_detector import GaugeDetector
from gauge_reader.src.config_manager import CalibrationConfig
import cv2
import os

config = CalibrationConfig('gauge_reader/calibrations/default_psi.json')
detector = GaugeDetector(config)

for img_file in os.listdir('gauge_reader/test_images'):
    frame = cv2.imread(f'gauge_reader/test_images/{img_file}')
    results = detector.process_frame(frame)
    print(f'{img_file}: {results[\"pressure\"]} PSI')
"
```

## Conclusion

You now have a fully functional real-time analog gauge reader! 

Next steps:
1. Calibrate your specific gauges
2. Optimize for your lighting conditions
3. Integrate with FireDesk dashboard
4. Fine-tune parameters for accuracy/speed trade-off

For detailed parameter tuning, see [TUNING_GUIDE.md](TUNING_GUIDE.md)
