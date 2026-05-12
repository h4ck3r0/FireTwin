#!/usr/bin/env python3
"""
Simple gauge detector for processing individual images
Used by the web API for real-time detection
"""

import sys
import os
import json
import cv2

# Add paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gauge_detector import GaugeDetector
from src.config_manager import CalibrationConfig

def detect_gauge_in_image(image_path: str, calibration_path: str = None):
    """
    Detect gauge in a single image and return results as JSON
    """
    try:
        # Load calibration
        calibration_path = calibration_path or os.path.join(
            os.path.dirname(__file__),
            'calibrations/default_psi.json'
        )
        
        config = CalibrationConfig(calibration_path)
        if not config.validate():
            return {
                "error": "Invalid calibration",
                "detection_success": False,
                "pressure": 0,
                "unit": "PSI"
            }
        
        # Load image
        frame = cv2.imread(image_path)
        if frame is None:
            return {
                "error": "Could not read image",
                "detection_success": False,
                "pressure": 0,
                "unit": "PSI"
            }
        
        # Detect gauge
        detector = GaugeDetector(config)
        results = detector.process_frame(frame)
        
        # Format output
        return {
            "pressure": results.get('pressure', 0),
            "unit": results.get('pressure_unit', 'PSI'),
            "angle_degrees": results.get('angle_degrees', 0),
            "detection_success": results.get('success', False),
            "gauge_name": config.get('gauge_name'),
            "timestamp": __import__('time').time()
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "detection_success": False,
            "pressure": 0,
            "unit": "PSI",
            "timestamp": __import__('time').time()
        }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Image path required",
            "detection_success": False
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    result = detect_gauge_in_image(image_path)
    print(json.dumps(result))
