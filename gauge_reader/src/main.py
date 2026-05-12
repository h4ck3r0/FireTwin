"""
Main real-time analog gauge reader.
Captures webcam video, detects gauge and needle, and displays pressure readings.

Usage:
    python main.py --calibration calibrations/default_psi.json
    python main.py --calibrate  # Run calibration wizard first
"""

import cv2
import argparse
import sys
import os
import numpy as np
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Handle both relative and absolute imports
try:
    from gauge_detector import GaugeDetector
    from config_manager import CalibrationConfig, create_default_calibrations
    from calibrator import GaugeCalibrator, interactive_calibration_wizard
    from utils import FPSCounter, smooth_value
except ImportError:
    from src.gauge_detector import GaugeDetector
    from src.config_manager import CalibrationConfig, create_default_calibrations
    from src.calibrator import GaugeCalibrator, interactive_calibration_wizard
    from src.utils import FPSCounter, smooth_value


class RealTimeGaugeReader:
    """
    Real-time analog gauge reader application.
    
    Handles:
    - Video capture
    - Frame processing
    - Result display
    - Keyboard controls
    - FPS tracking
    """
    
    def __init__(self, calibration_path: str = None, use_calibrator: bool = False):
        """
        Initialize gauge reader application.
        
        Args:
            calibration_path (str, optional): Path to calibration JSON file
            use_calibrator (bool): If True, run calibration wizard
        """
        self.fps_counter = FPSCounter()
        self.calibration_path = calibration_path
        self.use_calibrator = use_calibrator
        
        # Initialize configuration
        self.config = None
        self.detector = None
        self.calibrator = None
        
        # Smoothing for pressure readings
        self.last_pressure = None
        self.smoothing_alpha = 0.7  # 0.7 = responsive, 0.3 = smooth
        
        # Application state
        self.running = True
        self.calibration_mode = False
        self.paused = False
        
        # Statistics
        self.frames_processed = 0
        self.detections_successful = 0
    
    def initialize(self) -> bool:
        """
        Initialize the application.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "=" * 70)
        print("REAL-TIME ANALOG GAUGE READER")
        print("=" * 70)
        
        # Create default calibrations if needed
        print("\nInitializing calibration files...")
        create_default_calibrations()
        
        # Load or run calibration
        if self.use_calibrator:
            print("\nStarting calibration wizard...")
            if not interactive_calibration_wizard():
                return False
            self.config = CalibrationConfig()
        else:
            # Load calibration file
            if not self.calibration_path:
                # Try default PSI calibration
                default_path = os.path.join(
                    os.path.dirname(__file__), 
                    'calibrations', 
                    'default_psi.json'
                )
                if os.path.exists(default_path):
                    self.calibration_path = default_path
                else:
                    print("ERROR: No calibration file specified and default not found")
                    return False
            
            print(f"\nLoading calibration: {self.calibration_path}")
            self.config = CalibrationConfig(self.calibration_path)
            
            if not self.config.validate():
                print("ERROR: Calibration validation failed")
                return False
        
        self.config.print_summary()
        
        # Initialize detector
        self.detector = GaugeDetector(self.config)
        self.calibrator = GaugeCalibrator(self.config, self.detector)
        
        print("✓ Application initialized successfully")
        print("\nKeyboard Controls:")
        print("  'q'        - Quit")
        print("  'c'        - Enter calibration mode")
        print("  'space'    - Pause/Resume")
        print("  's'        - Save current frame")
        print("  'r'        - Reset to normal mode")
        print("  'ENTER'    - Confirm action in calibration mode")
        print("\n" + "=" * 70 + "\n")
        
        return True
    
    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Process a single video frame.
        
        Args:
            frame (np.ndarray): Input frame (BGR)
        
        Returns:
            dict: Processing results
        """
        self.frames_processed += 1
        
        # Detect gauge and needle
        results = self.detector.process_frame(frame)
        
        if results['success']:
            self.detections_successful += 1
            
            # Apply smoothing to pressure reading
            if results['pressure'] is not None:
                results['pressure'] = smooth_value(
                    results['pressure'],
                    self.last_pressure,
                    alpha=self.smoothing_alpha
                )
                self.last_pressure = results['pressure']
        
        return results
    
    def draw_frame(self, frame: np.ndarray, results: dict) -> np.ndarray:
        """
        Draw annotations and information on frame.
        
        Args:
            frame (np.ndarray): Input frame
            results (dict): Detection results
        
        Returns:
            np.ndarray: Annotated frame
        """
        height, width = frame.shape[:2]
        
        # Draw detection results
        if results['success']:
            frame = self.detector.draw_detection_results(frame, results)
        
        # Draw FPS and statistics
        fps = self.fps_counter.get_fps()
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(frame, fps_text, (width - 250, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw detection rate
        if self.frames_processed > 0:
            detection_rate = (self.detections_successful / self.frames_processed) * 100
            rate_text = f"Detection: {detection_rate:.1f}%"
            cv2.putText(frame, rate_text, (width - 250, 65),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw status indicators
        status_color = (0, 255, 0) if results['success'] else (0, 0, 255)
        status_text = "✓ DETECTING" if results['success'] else "✗ NO DETECTION"
        cv2.putText(frame, status_text, (width - 250, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Draw mode indicator
        if self.calibration_mode:
            cv2.putText(frame, "CALIBRATION MODE", (width - 400, height - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        if self.paused:
            cv2.putText(frame, "PAUSED", (width // 2 - 100, height // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        return frame
    
    def save_frame(self, frame: np.ndarray):
        """
        Save current frame to output directory.
        
        Args:
            frame (np.ndarray): Frame to save
        """
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"gauge_frame_{self.frames_processed}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        cv2.imwrite(filepath, frame)
        print(f"Frame saved: {filepath}")
    
    def handle_keyboard_input(self, key: int) -> bool:
        """
        Handle keyboard input.
        
        Args:
            key (int): Key code from cv2.waitKey()
        
        Returns:
            bool: True if should continue running, False to quit
        """
        key = key & 0xFF
        
        # Quit
        if key == ord('q'):
            print("\nShutting down...")
            return False
        
        # Calibration mode
        elif key == ord('c'):
            if not self.calibration_mode:
                print("\nEntering calibration mode... (Press 'q' to exit)")
                self.calibration_mode = True
                self.calibrator.reset()
            else:
                print("Exiting calibration mode...")
                self.calibration_mode = False
        
        # Pause/Resume
        elif key == ord(' '):
            self.paused = not self.paused
            status = "PAUSED" if self.paused else "RESUMED"
            print(f"{status}")
        
        # Save frame
        elif key == ord('s'):
            print("Saving frame...")
            self.save_frame_flag = True
        
        # Reset
        elif key == ord('r'):
            print("Reset to normal mode")
            self.calibration_mode = False
            self.paused = False
        
        # Calibration: Record minimum pressure
        elif key == 13 and self.calibration_mode:  # Enter key
            if self.calibrator.calibration_state == 'idle':
                status = self.calibrator.start_calibration
                print(f"Calibration: {status}")
            elif self.calibrator.calibration_state == 'waiting_min_pressure':
                print("Recording minimum pressure angle...")
            elif self.calibrator.calibration_state == 'waiting_max_pressure':
                print("Recording maximum pressure angle...")
        
        return True
    
    def run(self):
        """
        Main application loop.
        Captures video, processes frames, and displays results.
        """
        # Open video capture
        cap = cv2.VideoCapture("http://192.168.0.6:8080/video")
        
        if not cap.isOpened():
            print("ERROR: Cannot open video capture device")
            return False
        
        print("Video capture started (device 0)")
        print("Waiting for gauges to appear in frame...\n")
        
        self.save_frame_flag = False
        
        try:
            while self.running:
                ret, frame = cap.read()
                
                if not ret:
                    print("ERROR: Failed to read frame from camera")
                    break
                
                # Process frame if not paused
                if not self.paused:
                    if self.calibration_mode:
                        # Calibration mode processing
                        frame = self.calibrator.draw_calibration_ui(frame)
                        
                        # Try to detect gauge
                        if self.calibrator.calibration_state == 'idle':
                            gauge_info = self.detector.detect_gauge_circle(frame)
                            if gauge_info:
                                cx, cy, r = gauge_info
                                cv2.circle(frame, (cx, cy), r, (255, 255, 0), 2)
                                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                    else:
                        # Normal mode processing
                        results = self.process_frame(frame)

                        import json, time, os
                        status_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'public', 'gauge_status.json')
                        with open(status_path, 'w') as f:
                            json.dump({
                                "pressure": results.get('pressure') or 0,
                                "unit": "PSI",
                                "timestamp": time.time(),
                                "gauge_name": "Phone Camera",
                                "detection_success": results.get('success', False),
                                "angle_degrees": results.get('angle_degrees')
                            }, f)

                        frame = self.draw_frame(frame, results)
                        
                        # Save frame if requested
                        if self.save_frame_flag:
                            self.save_frame(frame)
                            self.save_frame_flag = False
                    
                    self.fps_counter.update()
                
                # Display frame
                cv2.imshow('Real-Time Gauge Reader', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1)
                if key != -1:
                    if not self.handle_keyboard_input(key):
                        break
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.print_statistics()
    
    def print_statistics(self):
        """Print runtime statistics."""
        print("\n" + "=" * 70)
        print("RUNTIME STATISTICS")
        print("=" * 70)
        print(f"Total frames processed:    {self.frames_processed}")
        print(f"Successful detections:     {self.detections_successful}")
        print(f"Detection rate:            {(self.detections_successful / max(self.frames_processed, 1) * 100):.1f}%")
        print(f"Average FPS:               {self.fps_counter.get_fps():.1f}")
        print("=" * 70 + "\n")


def main():
    """
    Main entry point.
    Parses command line arguments and starts the application.
    """
    parser = argparse.ArgumentParser(
        description='Real-time analog pressure gauge reader using OpenCV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --calibration calibrations/default_psi.json
  python main.py --calibration calibrations/default_bar.json
  python main.py --calibrate
        '''
    )
    
    parser.add_argument(
        '--calibration',
        type=str,
        help='Path to calibration JSON file'
    )
    
    parser.add_argument(
        '--calibrate',
        action='store_true',
        help='Run interactive calibration wizard'
    )
    
    parser.add_argument(
        '--list-calibrations',
        action='store_true',
        help='List available calibration files'
    )
    
    args = parser.parse_args()
    
    # List calibrations
    if args.list_calibrations:
        calibrations_dir = os.path.join(os.path.dirname(__file__), 'calibrations')
        if os.path.exists(calibrations_dir):
            files = [f for f in os.listdir(calibrations_dir) if f.endswith('.json')]
            print("\nAvailable calibrations:")
            for f in files:
                print(f"  - {f}")
        return
    
    # Initialize application
    app = RealTimeGaugeReader(
        calibration_path=args.calibration,
        use_calibrator=args.calibrate
    )
    
    if not app.initialize():
        print("Failed to initialize application")
        return
    
    # Run application
    app.run()


if __name__ == '__main__':
    
    main()
