# Installation & First Run Guide

## ✨ Complete! System Ready to Use

The real-time analog pressure gauge reader has been fully integrated into your FireDesk project.

### 📦 What's Installed

```
FireDesk/gauge_reader/
├── src/
│   ├── main.py                  (420 lines) - Real-time detection
│   ├── gauge_detector.py        (280 lines) - Hough transforms
│   ├── config_manager.py        (320 lines) - Configuration system
│   ├── calibrator.py            (220 lines) - Interactive calibration
│   └── utils.py                 (260 lines) - Utilities & helpers
│
├── calibrations/
│   ├── default_psi.json         - 0-100 PSI gauges
│   ├── default_bar.json         - 0-10 bar gauges
│   └── default_kpa.json         - 0-1000 kPa gauges
│
├── Documentation/
│   ├── README.md                - Overview
│   ├── TUTORIAL.md              - Complete guide
│   ├── TUNING_GUIDE.md          - Parameter reference
│   ├── ARCHITECTURE.md          - Technical details
│   └── PROJECT_SUMMARY.md       - Project overview
│
└── Tools/
    ├── setup.sh                 - Automated setup
    ├── QUICKSTART.py            - Interactive reference
    ├── examples.py              - Advanced examples
    └── firedesk_integration.py  - Dashboard integration
```

## 🚀 Quick Start (2 minutes)

### Step 1: Install Dependencies

```bash
cd /home/h4ck3r/Projects/FireDesk/gauge_reader
pip install -r requirements.txt
```

Or use the automated setup:

```bash
bash setup.sh
```

### Step 2: Run Real-Time Detection

```bash
python src/main.py --calibration calibrations/default_psi.json
```

**You should see:**
- Live webcam feed
- Cyan circle around the gauge
- Red line showing the needle
- Angle and pressure readings in green
- FPS counter

### Step 3: Test with Different Gauges

```bash
# For bar gauges
python src/main.py --calibration calibrations/default_bar.json

# For kPa gauges
python src/main.py --calibration calibrations/default_kpa.json
```

## 📚 Documentation Map

| File | Content | Time |
|------|---------|------|
| [README.md](README.md) | Quick overview | 2 min |
| [TUTORIAL.md](TUTORIAL.md) | Step-by-step guide | 15 min |
| [TUNING_GUIDE.md](TUNING_GUIDE.md) | Parameter optimization | 10 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical deep-dive | 20 min |
| [INDEX.md](INDEX.md) | Documentation index | 5 min |

## ⚙️ Recommended Reading Order

1. **First 5 minutes**: Read [README.md](README.md)
2. **Next 5 minutes**: Run `python QUICKSTART.py`
3. **First usage**: Follow [TUTORIAL.md](TUTORIAL.md) Part 1-3
4. **Calibrating your gauge**: Follow [TUTORIAL.md](TUTORIAL.md) Part 2
5. **Optimizing for your environment**: Read [TUNING_GUIDE.md](TUNING_GUIDE.md)

## 🎮 Keyboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit |
| `c` | Enter calibration mode |
| `SPACE` | Pause/Resume |
| `s` | Save frame |
| `r` | Reset |

## 🔧 Common Commands

```bash
# List all calibrations
python src/main.py --list-calibrations

# Interactive calibration
python src/main.py --calibrate

# Integration with FireDesk
python firedesk_integration.py

# View interactive reference
python QUICKSTART.py

# Run advanced examples
python examples.py
```

## ✅ Verification Checklist

After installation, verify everything works:

```bash
# Check Python modules compile
python3 -m py_compile src/*.py

# Test imports
python3 -c "from src.gauge_detector import GaugeDetector; print('✓ OK')"

# Test calibrations exist
ls calibrations/*.json

# Test video capture
python3 -c "import cv2; print('OpenCV', cv2.__version__)"
```

## 🎯 Next Steps

### For Quick Testing
```bash
python src/main.py --calibration calibrations/default_psi.json
```

### For Your Specific Gauge
```bash
python src/main.py --calibrate
# Follow the interactive wizard
```

### For Dashboard Integration
```bash
python firedesk_integration.py
```

### For Parameter Tuning
- Read [TUNING_GUIDE.md](TUNING_GUIDE.md)
- Edit calibration JSON files in `calibrations/`
- Test and iterate

## 🆘 Troubleshooting

### Issue: "Cannot find module"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Cannot open video capture"
```bash
# Check webcam
ls /dev/video*

# Or use different device ID
# See QUICKSTART.py for help
```

### Issue: Circle/needle not detected
- See [TUNING_GUIDE.md](TUNING_GUIDE.md) - "Common Issues"
- Improve lighting
- Adjust parameters in calibration JSON

## 📞 Help & Support

- **Quick reference**: `python QUICKSTART.py`
- **Installation help**: See this file
- **Usage guide**: [TUTORIAL.md](TUTORIAL.md)
- **Parameter tuning**: [TUNING_GUIDE.md](TUNING_GUIDE.md)
- **Technical details**: [ARCHITECTURE.md](ARCHITECTURE.md)

## ✨ You're Ready!

The system is fully installed and ready to use. Start with:

```bash
cd /home/h4ck3r/Projects/FireDesk/gauge_reader
python src/main.py --calibration calibrations/default_psi.json
```

Enjoy real-time analog gauge reading! 📊✨
