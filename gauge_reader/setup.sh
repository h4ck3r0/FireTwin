#!/bin/bash

# Real-Time Analog Gauge Reader - Installation & Setup Script
# This script sets up the gauge reader system and performs basic checks

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║      FIREDESK GAUGE READER - INSTALLATION & SETUP SCRIPT                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo "📦 Project Directory: $PROJECT_DIR"
echo ""

# Check Python installation
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment (optional but recommended)
echo "🔨 Setting up virtual environment..."
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Creating venv..."
    python3 -m venv "$PROJECT_DIR/venv"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$PROJECT_DIR/venv/bin/activate"
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "📚 Installing Python dependencies..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -q -r "$PROJECT_DIR/requirements.txt"
    echo "✓ Dependencies installed"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi
echo ""

# Verify OpenCV installation
echo "🔍 Verifying OpenCV installation..."
if python3 -c "import cv2; print(f'OpenCV {cv2.__version__}')" 2>/dev/null; then
    echo "✓ OpenCV verified"
else
    echo "❌ OpenCV import failed"
    exit 1
fi
echo ""

# Check webcam
echo "🎥 Checking webcam access..."
if python3 << 'EOF'
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    cap.release()
    print("✓ Webcam accessible (device 0)")
    exit(0)
else:
    print("⚠ Webcam not accessible (device 0)")
    print("  Available devices: /dev/video*")
    exit(1)
EOF
then
    WEBCAM_OK=true
else
    echo "  Continuing anyway - you may need to connect webcam or adjust device ID"
    WEBCAM_OK=false
fi
echo ""

# Create calibrations if they don't exist
echo "📋 Ensuring calibration files exist..."
if [ -d "$PROJECT_DIR/calibrations" ]; then
    FILE_COUNT=$(find "$PROJECT_DIR/calibrations" -name "*.json" | wc -l)
    echo "✓ Found $FILE_COUNT calibration files"
else
    echo "Creating calibrations directory..."
    mkdir -p "$PROJECT_DIR/calibrations"
    echo "✓ Calibrations directory created"
fi

# Create output directory
echo "Creating output directory..."
mkdir -p "$PROJECT_DIR/output"
echo "✓ Output directory ready"
echo ""

# Run verification script
echo "✅ Running verification tests..."
python3 << 'VERIFY_EOF'
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gauge_detector import GaugeDetector
    print("✓ gauge_detector module OK")
except Exception as e:
    print(f"✗ gauge_detector error: {e}")
    exit(1)

try:
    from config_manager import CalibrationConfig
    print("✓ config_manager module OK")
except Exception as e:
    print(f"✗ config_manager error: {e}")
    exit(1)

try:
    from calibrator import GaugeCalibrator
    print("✓ calibrator module OK")
except Exception as e:
    print(f"✗ calibrator error: {e}")
    exit(1)

try:
    from utils import FPSCounter, calculate_angle_from_line
    print("✓ utils module OK")
except Exception as e:
    print(f"✗ utils error: {e}")
    exit(1)

print("\n✅ All modules verified successfully!")
VERIFY_EOF

if [ $? -ne 0 ]; then
    echo "❌ Module verification failed"
    exit 1
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    SETUP COMPLETE ✅                                       ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "📖 Documentation:"
echo "   • README.md          - Overview"
echo "   • TUTORIAL.md        - Complete guide"
echo "   • TUNING_GUIDE.md    - Parameter reference"
echo "   • ARCHITECTURE.md    - Technical details"
echo ""

echo "🚀 Quick Start (in this terminal):"
echo ""
echo "   cd \"$PROJECT_DIR\""
echo "   source venv/bin/activate"
echo "   python src/main.py --calibration calibrations/default_psi.json"
echo ""

echo "📚 Additional Commands:"
echo ""
echo "   python src/main.py --help                    # Show all options"
echo "   python src/main.py --calibrate               # Interactive calibration"
echo "   python src/main.py --list-calibrations       # List available gauges"
echo "   python firedesk_integration.py               # Dashboard integration"
echo "   python examples.py                           # Advanced examples"
echo ""

echo "⚙️  Configuration:"
echo "   • Calibration files: calibrations/"
echo "   • Output files:      output/"
echo "   • Python modules:    src/"
echo ""

if [ "$WEBCAM_OK" = true ]; then
    echo "✅ Webcam detected - Ready to start!"
else
    echo "⚠️  Webcam not detected - Connect webcam and try: python src/main.py --help"
fi

echo ""
echo "For help, see: python QUICKSTART.py"
echo ""
