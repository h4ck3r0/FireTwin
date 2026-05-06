"""
Interactive calibration system for analog pressure gauges.
Allows users to manually calibrate gauges by identifying key reference points.
"""

import cv2
import numpy as np
from typing import Optional, Tuple

# Handle both relative and absolute imports
try:
    from .gauge_detector import GaugeDetector
    from .config_manager import CalibrationConfig
except ImportError:
    from gauge_detector import GaugeDetector
    from config_manager import CalibrationConfig


class GaugeCalibrator:
    """
    Interactive calibration tool for analog pressure gauges.
    
    Calibration process:
    1. User identifies minimum pressure needle position
    2. System calculates angle at minimum pressure
    3. User identifies maximum pressure needle position
    4. System calculates angle at maximum pressure
    5. Configuration is saved
    """
    
    def __init__(self, config: CalibrationConfig, detector: GaugeDetector):
        """
        Initialize calibrator.
        
        Args:
            config (CalibrationConfig): Calibration configuration to update
            detector (GaugeDetector): Gauge detector instance
        """
        self.config = config
        self.detector = detector
        self.calibration_state = 'idle'
        self.min_angle = None
        self.max_angle = None
        self.gauge_center = None
        self.gauge_radius = None
    
    def start_calibration(self, frame: np.ndarray) -> str:
        """
        Start interactive calibration process.
        
        First, detects gauge circle to establish reference.
        
        Args:
            frame (np.ndarray): Input frame
        
        Returns:
            str: Status message
        """
        # Detect gauge circle
        gauge_info = self.detector.detect_gauge_circle(frame)
        
        if gauge_info is None:
            return "ERROR: Cannot detect gauge circle. Try adjusting Hough Circle parameters."
        
        self.gauge_center, self.gauge_radius = gauge_info[:2]
        self.calibration_state = 'waiting_min_pressure'
        
        return f"Gauge detected at {self.gauge_center} with radius {self.gauge_radius}px\nPoint needle at MINIMUM pressure position and press ENTER"
    
    def record_min_pressure(self, frame: np.ndarray) -> str:
        """
        Record needle angle at minimum pressure.
        
        User should position the needle at the gauge's minimum pressure marking
        before calling this function.
        
        Args:
            frame (np.ndarray): Input frame with needle at minimum pressure
        
        Returns:
            str: Status message
        """
        if self.calibration_state != 'waiting_min_pressure':
            return "ERROR: Not in correct calibration state"
        
        needle_line = self.detector.detect_needle_line(frame, self.gauge_center, self.gauge_radius)
        
        if needle_line is None:
            return "ERROR: Cannot detect needle. Adjust Canny thresholds or check lighting."
        
        self.min_angle = self.detector.calculate_needle_angle(needle_line, self.gauge_center)
        self.calibration_state = 'waiting_max_pressure'
        
        return f"Minimum pressure angle recorded: {self.min_angle:.1f}°\nPoint needle at MAXIMUM pressure position and press ENTER"
    
    def record_max_pressure(self, frame: np.ndarray) -> str:
        """
        Record needle angle at maximum pressure.
        
        User should position the needle at the gauge's maximum pressure marking.
        
        Args:
            frame (np.ndarray): Input frame with needle at maximum pressure
        
        Returns:
            str: Status message
        """
        if self.calibration_state != 'waiting_max_pressure':
            return "ERROR: Not in correct calibration state"
        
        needle_line = self.detector.detect_needle_line(frame, self.gauge_center, self.gauge_radius)
        
        if needle_line is None:
            return "ERROR: Cannot detect needle. Adjust Canny thresholds or check lighting."
        
        self.max_angle = self.detector.calculate_needle_angle(needle_line, self.gauge_center)
        self.calibration_state = 'complete'
        
        return f"Maximum pressure angle recorded: {self.max_angle:.1f}°\nCalibration complete!"
    
    def finalize_calibration(self) -> bool:
        """
        Save calibration results to configuration.
        
        Updates min_angle and max_angle in configuration.
        Must be called after both min and max angles are recorded.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.calibration_state != 'complete':
            print("ERROR: Calibration not complete")
            return False
        
        if self.min_angle is None or self.max_angle is None:
            print("ERROR: Missing calibration data")
            return False
        
        # Update configuration
        self.config.set('min_angle', round(self.min_angle, 2))
        self.config.set('max_angle', round(self.max_angle, 2))
        
        print(f"\nCalibration Results:")
        print(f"  Min angle: {self.min_angle:.2f}°")
        print(f"  Max angle: {self.max_angle:.2f}°")
        print(f"  Angle range: {abs(self.max_angle - self.min_angle):.2f}°")
        
        return True
    
    def reset(self):
        """Reset calibration state."""
        self.calibration_state = 'idle'
        self.min_angle = None
        self.max_angle = None
        self.gauge_center = None
        self.gauge_radius = None
    
    def draw_calibration_ui(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw calibration UI on frame.
        
        Shows instructions and current calibration state.
        
        Args:
            frame (np.ndarray): Input frame
        
        Returns:
            np.ndarray: Frame with UI drawn
        """
        height, width = frame.shape[:2]
        
        # Draw semi-transparent overlay for text background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (width - 10, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Draw state text
        state_text = f"CALIBRATION MODE: {self.calibration_state.upper()}"
        cv2.putText(frame, state_text, (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        if self.calibration_state == 'waiting_min_pressure':
            instruction = "Point needle at MINIMUM pressure, then press ENTER"
            cv2.putText(frame, instruction, (20, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        elif self.calibration_state == 'waiting_max_pressure':
            instruction = "Point needle at MAXIMUM pressure, then press ENTER"
            cv2.putText(frame, instruction, (20, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            angle_text = f"Min angle: {self.min_angle:.1f}°"
            cv2.putText(frame, angle_text, (20, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)
        
        elif self.calibration_state == 'complete':
            result_text = f"Calibration Complete! Min: {self.min_angle:.1f}°  Max: {self.max_angle:.1f}°"
            cv2.putText(frame, result_text, (20, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            save_text = "Press 's' to save configuration"
            cv2.putText(frame, save_text, (20, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return frame


def interactive_calibration_wizard(config_path: Optional[str] = None) -> bool:
    """
    Run interactive calibration wizard.
    
    Step-by-step guide for user to calibrate a new gauge.
    
    Args:
        config_path (str, optional): Path to save calibration file
    
    Returns:
        bool: True if calibration successful, False if cancelled
    """
    print("\n" + "=" * 70)
    print("ANALOG GAUGE CALIBRATION WIZARD")
    print("=" * 70)
    
    # Get gauge information from user
    print("\nEnter gauge information:")
    gauge_name = input("Gauge name (e.g., 'Pump Pressure'): ") or "Unknown Gauge"
    unit = input("Unit (PSI/bar/kPa): ") or "PSI"
    min_pressure = float(input("Minimum pressure value: ") or 0)
    max_pressure = float(input("Maximum pressure value: ") or 100)
    
    # Create configuration
    config = CalibrationConfig()
    config.set('gauge_name', gauge_name)
    config.set('unit', unit)
    config.set('min_pressure', min_pressure)
    config.set('max_pressure', max_pressure)
    
    # Create detector and calibrator
    detector = GaugeDetector(config)
    calibrator = GaugeCalibrator(config, detector)
    
    # Open video capture
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Cannot open video capture device")
        return False
    
    print("\nStarting video capture... Press 'q' to cancel, 'ENTER' to proceed at each step")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Start calibration
            if calibrator.calibration_state == 'idle':
                status = calibrator.start_calibration(frame)
                print(status)
            
            # Draw calibration UI
            frame = calibrator.draw_calibration_ui(frame)
            
            # Draw gauge detection if available
            if calibrator.gauge_center:
                cx, cy = calibrator.gauge_center
                radius = calibrator.gauge_radius
                cv2.circle(frame, (cx, cy), radius, (255, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            
            # Display frame
            cv2.imshow('Gauge Calibration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Calibration cancelled")
                return False
            
            elif key == 13:  # Enter key
                if calibrator.calibration_state == 'waiting_min_pressure':
                    status = calibrator.record_min_pressure(frame)
                    print(status)
                
                elif calibrator.calibration_state == 'waiting_max_pressure':
                    status = calibrator.record_max_pressure(frame)
                    print(status)
                
                elif calibrator.calibration_state == 'complete':
                    if calibrator.finalize_calibration():
                        # Save configuration
                        save_path = config_path or f"calibrations/{gauge_name.replace(' ', '_')}.json"
                        config.save_to_file(save_path)
                        print(f"\nCalibration saved to: {save_path}")
                        config.print_summary()
                        return True
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    return False
