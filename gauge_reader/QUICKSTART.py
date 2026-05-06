"""
Quick Start & Project Summary
Complete gauge reader system integrated into FireDesk project.
"""

import os
import sys
import json

# Display project structure
def print_project_structure():
    """Print the gauge reader project structure."""
    
    structure = """
    
╔════════════════════════════════════════════════════════════════════════════╗
║          FIREDESK GAUGE READER - PROJECT STRUCTURE & SETUP                ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 FireDesk/ (Main Project Root)
│
├── gauge_reader/                   ← NEW: Real-Time Analog Gauge Reader
│   ├── src/                        ← Core Python modules
│   │   ├── __init__.py            ← Package initialization
│   │   ├── main.py                ← Entry point (real-time processing)
│   │   ├── gauge_detector.py      ← Hough Circle/Line transforms
│   │   ├── config_manager.py      ← JSON calibration management
│   │   ├── calibrator.py          ← Interactive calibration wizard
│   │   └── utils.py               ← Helper functions (angle calc, FPS)
│   │
│   ├── calibrations/               ← Gauge calibration files
│   │   ├── default_psi.json       ← 0-100 PSI gauge
│   │   ├── default_bar.json       ← 0-10 bar gauge
│   │   └── default_kpa.json       ← 0-1000 kPa gauge
│   │
│   ├── output/                    ← Generated outputs
│   │   └── (saved frames & logs)
│   │
│   ├── test_images/               ← Test gauge images
│   │
│   ├── requirements.txt            ← Python dependencies
│   ├── README.md                   ← Overview
│   ├── TUTORIAL.md                ← Step-by-step guide
│   ├── TUNING_GUIDE.md            ← Parameter optimization
│   ├── ARCHITECTURE.md            ← Technical documentation
│   ├── firedesk_integration.py    ← Dashboard integration
│   └── examples.py                 ← Advanced usage examples
│
├── src/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── AdvancedFeatures.tsx
│   │   ├── ControlPanel.tsx
│   │   ├── EmergencyMode.tsx
│   │   ├── FireReadinessCard.tsx
│   │   ├── PumpCard.tsx
│   │   ├── PumpSystem2D.tsx
│   │   ├── PumpSystemRealistic.tsx
│   │   ├── RadialGauge.tsx
│   │   ├── SupportSystemRow.tsx
│   │   ├── SystemAlerts.tsx
│   │   ├── SystemPerformance.tsx
│   │   └── pumpRoomEngine.ts
│   └── lib/
│       └── pumpRoomEngine.ts
│
└── (other Next.js project files)

════════════════════════════════════════════════════════════════════════════════
"""
    
    print(structure)


# Installation instructions
def print_installation():
    """Print installation instructions."""
    
    instructions = """
╔════════════════════════════════════════════════════════════════════════════╗
║                       INSTALLATION & SETUP                                ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: Install Python Dependencies
────────────────────────────────────

    cd /home/h4ck3r/Projects/FireDesk/gauge_reader
    pip install -r requirements.txt

This installs:
    ✓ opencv-python (4.8.1.78)
    ✓ numpy (1.24.3)
    ✓ json5 (0.9.14)

Verify installation:
    python -c "import cv2; print(cv2.__version__)"


STEP 2: Test Your Webcam
────────────────────────

    python -c "
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print('Webcam OK' if ret else 'Webcam NOT WORKING')
cap.release()
    "


STEP 3: Quick Start (30 seconds)
────────────────────────────────

    python src/main.py --calibration calibrations/default_psi.json

You should see:
    ✓ Live video feed
    ✓ Cyan circle around gauge
    ✓ Red line showing needle
    ✓ Angle and pressure readings
    ✓ FPS counter


STEP 4: Calibrate Your Gauge
────────────────────────────

    python src/main.py --calibrate

Follow the wizard:
    1. Enter gauge name
    2. Enter pressure unit (PSI/bar/kPa)
    3. Enter pressure range
    4. Point needle at minimum pressure → Press ENTER
    5. Point needle at maximum pressure → Press ENTER
    6. Configuration automatically saved


STEP 5: Integrate with FireDesk
───────────────────────────────

See firedesk_integration.py for:
    - UDP socket communication
    - JSON file updates
    - Real-time pressure streaming

════════════════════════════════════════════════════════════════════════════════
"""
    
    print(instructions)


# Usage examples
def print_usage_examples():
    """Print common usage examples."""
    
    examples = """
╔════════════════════════════════════════════════════════════════════════════╗
║                           USAGE EXAMPLES                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

EXAMPLE 1: Default PSI Gauge
──────────────────────────────────────────────────────────────────────────────

    cd /home/h4ck3r/Projects/FireDesk/gauge_reader
    python src/main.py --calibration calibrations/default_psi.json

    Expected: Pressure in 0-100 PSI range


EXAMPLE 2: Other Gauge Types
──────────────────────────────────────────────────────────────────────────────

For bar gauge:
    python src/main.py --calibration calibrations/default_bar.json

For kPa gauge:
    python src/main.py --calibration calibrations/default_kpa.json


EXAMPLE 3: Custom Gauge Calibration
──────────────────────────────────────────────────────────────────────────────

Interactive wizard:
    python src/main.py --calibrate

Then use:
    python src/main.py --calibration calibrations/My_Gauge.json


EXAMPLE 4: List Available Calibrations
──────────────────────────────────────────────────────────────────────────────

    python src/main.py --list-calibrations


EXAMPLE 5: FireDesk Integration
──────────────────────────────────────────────────────────────────────────────

    python firedesk_integration.py

This streams gauge readings to FireDesk dashboard


EXAMPLE 6: Advanced Processing (Batch/Video)
──────────────────────────────────────────────────────────────────────────────

    python examples.py

Choose from:
    - Batch image processing
    - Video file processing
    - Smoothed real-time reading
    - Pressure range monitoring
    - Multi-calibration comparison
    - Angle detection mode

════════════════════════════════════════════════════════════════════════════════
"""
    
    print(examples)


# Keyboard controls
def print_keyboard_controls():
    """Print keyboard control reference."""
    
    controls = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          KEYBOARD CONTROLS                                ║
╚════════════════════════════════════════════════════════════════════════════╝

During Normal Operation:
───────────────────────

    q           Quit application
    c           Enter calibration mode
    SPACE       Pause/Resume video
    s           Save current frame to output/
    r           Reset to normal mode


During Calibration Mode:
────────────────────────

    ENTER       Confirm current step
                  (position needle first)
    q           Cancel calibration


Real-Time Display Shows:
────────────────────────

    FPS         Frames per second (target: 25-30+)
    Detection   % of frames with successful gauge detection
    Status      ✓ DETECTING or ✗ NO DETECTION
    Angle       Needle angle in degrees (0-360°)
    Pressure    Calculated pressure in configured unit

════════════════════════════════════════════════════════════════════════════════
"""
    
    print(controls)


# Calibration parameters
def print_calibration_parameters():
    """Print calibration parameter reference."""
    
    params = """
╔════════════════════════════════════════════════════════════════════════════╗
║                       CALIBRATION PARAMETERS                              ║
╚════════════════════════════════════════════════════════════════════════════╝

Required Parameters (for any gauge):
─────────────────────────────────────

    gauge_name              String describing the gauge
    unit                    Pressure unit: PSI, bar, or kPa
    min_angle              Angle (°) at minimum pressure (typically 45°)
    max_angle              Angle (°) at maximum pressure (typically 315°)
    min_pressure           Minimum pressure value
    max_pressure           Maximum pressure value


Optional Tuning Parameters (default values work for most):
──────────────────────────────────────────────────────────

Circle Detection (Hough):
    hough_circles_param1   [100]     Canny threshold (lower = detect fainter)
    hough_circles_param2   [30]      Accumulator threshold (lower = more circles)
    hough_circles_minRadius [50]     Minimum gauge radius in pixels
    hough_circles_maxRadius [300]    Maximum gauge radius in pixels

Edge Detection (Canny):
    canny_threshold1       [50]      Lower edge threshold
    canny_threshold2       [150]     Upper edge threshold

Preprocessing:
    gaussian_kernel        [15, 15]  Blur kernel size (must be odd)

Line Detection (Hough):
    hough_lines_minLineLength [50]   Minimum needle length
    hough_lines_maxLineGap    [10]   Maximum gap in needle line


Example Custom Gauge Configuration:
────────────────────────────────────

{
  "gauge_name": "Pump Suction Pressure",
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

════════════════════════════════════════════════════════════════════════════════
"""
    
    print(params)


# Troubleshooting
def print_troubleshooting():
    """Print troubleshooting guide."""
    
    troubleshooting = """
╔════════════════════════════════════════════════════════════════════════════╗
║                           TROUBLESHOOTING                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

PROBLEM: "Cannot open video capture device"
────────────────────────────────────────────────────────────────────────────

Solution:
    1. Verify webcam is connected: ls /dev/video*
    2. Test with: python -c "import cv2; cv2.VideoCapture(0).isOpened()"
    3. Try different device ID: VideoCapture(1) or VideoCapture(2)
    4. On Linux: sudo apt install libsm6 libxext6


PROBLEM: Circle Not Detected
────────────────────────────────────────────────────────────────────────────

Solution:
    1. Improve lighting (use LED lamp)
    2. Decrease param2: "hough_circles_param2": 20
    3. Increase blur kernel: "gaussian_kernel": [21, 21]
    4. Widen radius range: "hough_circles_minRadius": 30
    5. Check gauge is in frame


PROBLEM: Needle Not Detected
────────────────────────────────────────────────────────────────────────────

Solution:
    1. Decrease Canny thresholds:
       "canny_threshold1": 30
       "canny_threshold2": 100
    2. Decrease needle minimum length: "hough_lines_minLineLength": 30
    3. Improve lighting and contrast
    4. Run calibration again with better positioning


PROBLEM: Very Low FPS (< 5)
────────────────────────────────────────────────────────────────────────────

Solution:
    1. Reduce blur kernel: "gaussian_kernel": [11, 11]
    2. Increase param2: "hough_circles_param2": 50
    3. Close other applications
    4. Resize frames (see examples.py)


PROBLEM: Pressure Values Jump Around
────────────────────────────────────────────────────────────────────────────

Solution:
    1. Increase smoothing in src/main.py
    2. Find: alpha=0.7
    3. Change to: alpha=0.9 (more smoothing)
    4. Re-calibrate more carefully
    5. Improve lighting


PROBLEM: Detection Rate Very Low (< 50%)
────────────────────────────────────────────────────────────────────────────

Solution:
    1. Check lighting (minimum 500 lux recommended)
    2. Clean camera lens
    3. Decrease Canny thresholds
    4. Run full calibration: python src/main.py --calibrate
    5. Verify gauge is clearly visible in frame


PROBLEM: "AttributeError: module 'cv2' has no attribute..."
────────────────────────────────────────────────────────────────────────────

Solution:
    pip install --upgrade opencv-python


PROBLEM: "ModuleNotFoundError: No module named 'cv2'"
────────────────────────────────────────────────────────────────────────────

Solution:
    pip install -r requirements.txt


For more help:
    See TUTORIAL.md for step-by-step guide
    See TUNING_GUIDE.md for parameter optimization
    See ARCHITECTURE.md for technical details

════════════════════════════════════════════════════════════════════════════════
"""
    
    print(troubleshooting)


# Main info display
def print_full_guide():
    """Print complete guide."""
    
    print_project_structure()
    print_installation()
    print_usage_examples()
    print_keyboard_controls()
    print_calibration_parameters()
    print_troubleshooting()
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                        ADDITIONAL RESOURCES                               ║
╚════════════════════════════════════════════════════════════════════════════╝

📖 Documentation Files:
    ├─ README.md              - Project overview
    ├─ TUTORIAL.md            - Complete step-by-step tutorial
    ├─ TUNING_GUIDE.md        - Parameter optimization guide
    ├─ ARCHITECTURE.md        - Technical architecture & algorithms
    └─ This file              - Quick reference

🔧 Source Code:
    ├─ src/main.py            - Real-time processing entry point
    ├─ src/gauge_detector.py  - Hough Circle/Line transforms
    ├─ src/config_manager.py  - Calibration file management
    ├─ src/calibrator.py      - Interactive calibration
    ├─ src/utils.py           - Helper functions
    └─ examples.py            - Advanced usage examples

⚙️ Configuration:
    ├─ calibrations/default_psi.json  - PSI gauge (0-100)
    ├─ calibrations/default_bar.json  - bar gauge (0-10)
    ├─ calibrations/default_kpa.json  - kPa gauge (0-1000)
    └─ requirements.txt               - Python dependencies

🚀 Quick Start (Copy & Paste):
    
    cd /home/h4ck3r/Projects/FireDesk/gauge_reader
    pip install -r requirements.txt
    python src/main.py --calibration calibrations/default_psi.json

════════════════════════════════════════════════════════════════════════════════

✨ You're all set! Start with: python src/main.py --help

════════════════════════════════════════════════════════════════════════════════
""")


if __name__ == '__main__':
    print_full_guide()
