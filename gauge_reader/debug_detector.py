"""
Debug script to visualize gauge detection in real-time.
Shows intermediate detection steps to help tune parameters.
"""

import cv2
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from src.gauge_detector import GaugeDetector
    from src.config_manager import CalibrationConfig
except ImportError:
    from gauge_detector import GaugeDetector
    from config_manager import CalibrationConfig

def main():
    # Load calibration
    config_path = "calibrations/default_psi.json"
    if not Path(config_path).exists():
        print(f"❌ Config not found: {config_path}")
        return
    
    config = CalibrationConfig(config_path)
    detector = GaugeDetector(config)
    
    # Start webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return
    
    print("=" * 70)
    print("GAUGE DETECTOR - DEBUG MODE")
    print("=" * 70)
    print(f"✓ Loaded calibration: {config_path}")
    print(f"✓ Hough Circles Param1: {detector.config.get('hough_circles_param1')}")
    print(f"✓ Hough Circles Param2: {detector.config.get('hough_circles_param2')}")
    print(f"✓ Canny Threshold 1: {detector.config.get('canny_threshold1')}")
    print(f"✓ Canny Threshold 2: {detector.config.get('canny_threshold2')}")
    print("\nControls:")
    print("  'q' - Quit")
    print("  'space' - Pause/Resume")
    print("  '+' - Increase Param2 (detection sensitivity)")
    print("  '-' - Decrease Param2")
    print("  'u' - Increase Param1")
    print("  'd' - Decrease Param1")
    print("=" * 70)
    
    paused = False
    param2 = detector.config.get('hough_circles_param2', 30)
    param1 = detector.config.get('hough_circles_param1', 100)
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break
        
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # Detect gauge
        results = detector.process_frame(frame)
        
        # Create display frame
        display_frame = frame.copy()
        
        # Draw detection results
        if results['success']:
            # Draw circle
            cx, cy, r = results['gauge_center'][0], results['gauge_center'][1], results['gauge_radius']
            cv2.circle(display_frame, (int(cx), int(cy)), int(r), (0, 255, 255), 2)  # Cyan circle
            cv2.circle(display_frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)  # Red center
            
            # Draw needle
            if results['needle_line']:
                x1, y1, x2, y2 = results['needle_line']
                cv2.line(display_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)  # Red needle
            
            # Draw text
            angle = results['angle_degrees']
            pressure = results['pressure']
            cv2.putText(display_frame, f"Gauge Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Angle: {angle:.1f}°", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Pressure: {pressure:.1f} {config.get('unit')}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(display_frame, "❌ No gauge detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(display_frame, f"Param1: {param1}, Param2: {param2}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, "Try adjusting with +/- keys", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Show frame
        cv2.imshow('Gauge Detector - Debug Mode', display_frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('+'):
            param2 = min(param2 + 5, 100)
            detector.config.update({'hough_circles_param2': param2})
            print(f"✓ Param2 increased to {param2}")
        elif key == ord('-'):
            param2 = max(param2 - 5, 1)
            detector.config.update({'hough_circles_param2': param2})
            print(f"✓ Param2 decreased to {param2}")
        elif key == ord('u'):
            param1 = min(param1 + 5, 200)
            detector.config.update({'hough_circles_param1': param1})
            print(f"✓ Param1 increased to {param1}")
        elif key == ord('d'):
            param1 = max(param1 - 5, 1)
            detector.config.update({'hough_circles_param1': param1})
            print(f"✓ Param1 decreased to {param1}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Done")

if __name__ == "__main__":
    main()
