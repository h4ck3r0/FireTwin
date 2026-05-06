"""
Core gauge detection engine.
Handles Hough Circle and Hough Line transforms for detecting gauges and needles.
"""

import cv2
import numpy as np
import math
from typing import Tuple, Optional, List

# Handle both relative and absolute imports
try:
    from .utils import calculate_angle_from_line, line_length, point_to_line_distance
except ImportError:
    from utils import calculate_angle_from_line, line_length, point_to_line_distance


class GaugeDetector:
    """
    Detects analog pressure gauges and needles in images using OpenCV.
    
    Main operations:
    1. Detect circular gauge using Hough Circle Transform
    2. Detect needle line using Hough Line Transform
    3. Calculate needle angle relative to gauge center
    4. Convert angle to pressure using calibration
    """
    
    def __init__(self, config=None):
        """
        Initialize gauge detector.
        
        Args:
            config (CalibrationConfig, optional): Calibration configuration
        """
        self.config = config
        self.last_detected_circle = None
        self.last_detected_needle = None
        self.last_angle = None
        self.last_pressure = None
    
    def detect_gauge_circle(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """
        Detect circular gauge using Hough Circle Transform.
        
        Steps:
        1. Convert frame to grayscale
        2. Apply Gaussian blur to reduce noise
        3. Apply Hough Circle Transform
        4. Return circle with highest confidence
        
        Args:
            frame (np.ndarray): Input image frame (BGR)
        
        Returns:
            Tuple[int, int, int]: (center_x, center_y, radius) or None if not found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise and improve circle detection
        # Larger kernel = more blur = better for noisy images but slower
        blur_kernel = self.config.get('gaussian_kernel', (15, 15)) if self.config else (15, 15)
        blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
        
        # Get Hough Circle parameters from config
        if self.config:
            param1 = self.config.get('hough_circles_param1', 100)
            param2 = self.config.get('hough_circles_param2', 30)
            min_radius = self.config.get('hough_circles_minRadius', 50)
            max_radius = self.config.get('hough_circles_maxRadius', 300)
        else:
            param1, param2 = 100, 30
            min_radius, max_radius = 50, 300
        
        # Detect circles using Hough Circle Transform
        # Parameters:
        # - input: grayscale image
        # - cv2.HOUGH_GRADIENT: detection method
        # - dp: inverse ratio of accumulator resolution
        # - minDist: minimum distance between circles
        # - param1: Canny edge detection upper threshold
        # - param2: accumulator threshold for circle center
        # - minRadius, maxRadius: circle radius constraints
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=param1,
            param2=param2,
            minRadius=min_radius,
            maxRadius=max_radius
        )
        
        if circles is None or len(circles) == 0:
            return None
        
        # Convert to standard format and select largest/most prominent circle
        circles = np.uint16(np.around(circles))
        circle = circles[0][0]
        
        center_x, center_y, radius = int(circle[0]), int(circle[1]), int(circle[2])
        self.last_detected_circle = (center_x, center_y, radius)
        
        return center_x, center_y, radius
    
    def detect_needle_line(self, frame: np.ndarray, 
                          gauge_center: Tuple[int, int], 
                          gauge_radius: int) -> Optional[np.ndarray]:
        """
        Detect needle line using Hough Line Transform.
        
        Steps:
        1. Convert to grayscale
        2. Apply Canny edge detection
        3. Apply Hough Line Transform
        4. Filter lines near gauge center and pointing outward
        5. Select longest line as needle
        
        Args:
            frame (np.ndarray): Input image frame (BGR)
            gauge_center (Tuple[int, int]): (center_x, center_y) of gauge
            gauge_radius (int): Radius of detected gauge circle
        
        Returns:
            np.ndarray: Line coordinates (x1, y1, x2, y2) or None if not found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection using Canny algorithm
        # Lower threshold = more edges detected (might include noise)
        # Higher threshold = fewer edges (might miss faint needles)
        canny_threshold1 = self.config.get('canny_threshold1', 50) if self.config else 50
        canny_threshold2 = self.config.get('canny_threshold2', 150) if self.config else 150
        
        edges = cv2.Canny(gray, canny_threshold1, canny_threshold2)
        
        # Get Hough Line parameters
        if self.config:
            min_line_length = self.config.get('hough_lines_minLineLength', 50)
            max_line_gap = self.config.get('hough_lines_maxLineGap', 10)
        else:
            min_line_length, max_line_gap = 50, 10
        
        # Detect lines using Hough Line Transform (probabilistic version)
        # Parameters:
        # - rho: distance resolution in pixels
        # - theta: angle resolution in radians
        # - threshold: minimum votes to accept a line
        # - minLineLength: minimum line length
        # - maxLineGap: maximum gap to connect line segments
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=50,
            minLineLength=min_line_length,
            maxLineGap=max_line_gap
        )
        
        if lines is None or len(lines) == 0:
            return None
        
        # Filter lines: keep only those starting near gauge center
        center_x, center_y = gauge_center
        filtered_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Check if line passes near center
            dist_to_center = point_to_line_distance(center_x, center_y, x1, y1, x2, y2)
            
            # Accept lines within center region (within 20% of radius)
            if dist_to_center < gauge_radius * 0.2:
                filtered_lines.append(line)
        
        if not filtered_lines:
            return None
        
        # Select the longest line as the needle
        longest_line = max(filtered_lines, key=lambda line: line_length(line[0][0], line[0][1], line[0][2], line[0][3]))
        
        self.last_detected_needle = longest_line[0]
        return longest_line[0]
    
    def calculate_needle_angle(self, needle_line: np.ndarray, 
                              gauge_center: Tuple[int, int]) -> float:
        """
        Calculate needle angle relative to gauge center.
        
        Angle is measured from horizontal (right = 0°), counterclockwise.
        Range: 0-360 degrees
        
        Args:
            needle_line (np.ndarray): Line coordinates (x1, y1, x2, y2)
            gauge_center (Tuple[int, int]): (center_x, center_y) of gauge
        
        Returns:
            float: Angle in degrees (0-360)
        """
        # Reshape line to format expected by calculate_angle_from_line
        line_reshaped = np.array([needle_line])
        angle = calculate_angle_from_line(line_reshaped, gauge_center[0], gauge_center[1])
        
        self.last_angle = angle
        return angle
    
    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Process a single frame to detect gauge and needle.
        
        Complete pipeline:
        1. Detect gauge circle
        2. Detect needle line
        3. Calculate needle angle
        4. Convert angle to pressure using calibration
        
        Args:
            frame (np.ndarray): Input image frame (BGR)
        
        Returns:
            dict: Results dictionary with keys:
                - 'success': bool, True if both gauge and needle detected
                - 'gauge_center': (x, y) tuple
                - 'gauge_radius': int
                - 'needle_line': (x1, y1, x2, y2) array
                - 'angle_degrees': float
                - 'pressure': float (if config available)
                - 'pressure_unit': str (if config available)
        """
        results = {
            'success': False,
            'gauge_center': None,
            'gauge_radius': None,
            'needle_line': None,
            'angle_degrees': None,
            'pressure': None,
            'pressure_unit': None
        }
        
        # Detect gauge circle
        gauge_info = self.detect_gauge_circle(frame)
        if gauge_info is None:
            return results
        
        center_x, center_y, radius = gauge_info
        results['gauge_center'] = (center_x, center_y)
        results['gauge_radius'] = radius
        
        # Detect needle line
        needle_line = self.detect_needle_line(frame, (center_x, center_y), radius)
        if needle_line is None:
            return results
        
        results['needle_line'] = needle_line
        
        # Calculate angle
        angle = self.calculate_needle_angle(needle_line, (center_x, center_y))
        results['angle_degrees'] = angle
        
        # Convert to pressure if config available
        if self.config and self.config.validate():
            from .utils import convert_angle_to_pressure
            
            min_angle = self.config.get('min_angle')
            max_angle = self.config.get('max_angle')
            min_pressure = self.config.get('min_pressure')
            max_pressure = self.config.get('max_pressure')
            
            pressure = convert_angle_to_pressure(angle, min_angle, max_angle, min_pressure, max_pressure)
            results['pressure'] = pressure
            results['pressure_unit'] = self.config.get('unit', 'PSI')
        
        results['success'] = True
        return results
    
    def draw_detection_results(self, frame: np.ndarray, results: dict, 
                              draw_circle: bool = True, 
                              draw_needle: bool = True,
                              draw_center: bool = True) -> np.ndarray:
        """
        Draw detection results on frame.
        
        Draws:
        - Gauge circle (cyan)
        - Needle line (red)
        - Center point (blue)
        - Angle and pressure text
        
        Args:
            frame (np.ndarray): Input frame (will be modified)
            results (dict): Results from process_frame()
            draw_circle (bool): Draw circle outline
            draw_needle (bool): Draw needle line
            draw_center (bool): Draw center point
        
        Returns:
            np.ndarray: Frame with annotations
        """
        if not results['success']:
            return frame
        
        # Draw gauge circle
        if draw_circle and results['gauge_center']:
            center_x, center_y = results['gauge_center']
            radius = results['gauge_radius']
            cv2.circle(frame, (center_x, center_y), radius, (255, 255, 0), 2)  # Cyan circle
        
        # Draw center point
        if draw_center and results['gauge_center']:
            center_x, center_y = results['gauge_center']
            cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)  # Blue dot
        
        # Draw needle line
        if draw_needle and results['needle_line'] is not None:
            x1, y1, x2, y2 = results['needle_line']
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Red line
        
        # Draw text annotations
        y_offset = 30
        
        if results['angle_degrees'] is not None:
            angle_text = f"Angle: {results['angle_degrees']:.1f}°"
            cv2.putText(frame, angle_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            y_offset += 35
        
        if results['pressure'] is not None:
            pressure_text = f"Pressure: {results['pressure']:.1f} {results['pressure_unit']}"
            cv2.putText(frame, pressure_text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame
