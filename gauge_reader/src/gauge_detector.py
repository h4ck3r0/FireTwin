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
    from .utils import calculate_angle_from_line, line_length, point_to_line_distance, smooth_value, normalize_angle
except ImportError:
    from utils import calculate_angle_from_line, line_length, point_to_line_distance, smooth_value, normalize_angle

from collections import deque


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
        
        # Accuracy & Stability parameters
        self.circle_lock_frames = 0
        self.max_circle_lock = 30  # Increased to 30 frames (approx 3 seconds)
        self.smoothing_alpha = 0.08 # EVEN STRONGER SMOOTHING (0.08 = very slow/stable)
        self.circle_jump_threshold = 15 # Pixels
        self.angle_window = deque(maxlen=7) # Rolling window for median filtering
    
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
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
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
            # Circle Locking: Use last known circle if recently detected
            if self.last_detected_circle and self.circle_lock_frames < self.max_circle_lock:
                self.circle_lock_frames += 1
                return self.last_detected_circle
            return None
        
        # Convert to standard format and select largest/most prominent circle
        circles = np.uint16(np.around(circles))
        circle = circles[0][0]
        
        center_x, center_y, radius = int(circle[0]), int(circle[1]), int(circle[2])
        
        # Stability: If new circle is very close to old one, smooth it instead of jumping
        if self.last_detected_circle:
            lcx, lcy, lr = self.last_detected_circle
            dist = math.sqrt((center_x - lcx)**2 + (center_y - lcy)**2)
            if dist < self.circle_jump_threshold:
                center_x = int(smooth_value(center_x, lcx, 0.8))
                center_y = int(smooth_value(center_y, lcy, 0.8))
                radius = int(smooth_value(radius, lr, 0.8))
        
        self.last_detected_circle = (center_x, center_y, radius)
        self.circle_lock_frames = 0
        
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
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Apply edge detection using Canny algorithm
        # Lower threshold = more edges detected (might include noise)
        # Higher threshold = fewer edges (might miss faint needles)
        canny_threshold1 = self.config.get('canny_threshold1', 40) if self.config else 40
        canny_threshold2 = self.config.get('canny_threshold2', 120) if self.config else 120
        
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
        
        # Increase min line length relative to radius for better accuracy
        dynamic_min_line_length = gauge_radius * 0.4
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = line_length(x1, y1, x2, y2)
            
            if length < dynamic_min_line_length:
                continue
                
            # Check if line passes near center
            dist_to_center = point_to_line_distance(center_x, center_y, x1, y1, x2, y2)
            
            # Accept lines within center region (within 15% of radius)
            if dist_to_center < gauge_radius * 0.15:
                filtered_lines.append(line)
        
        if not filtered_lines:
            # If no new line, reuse last needle for stability
            if self.last_detected_needle is not None:
                return self.last_detected_needle
            return None
        
        # Select the longest line as the needle
        longest_line = max(filtered_lines, key=lambda line: line_length(line[0][0], line[0][1], line[0][2], line[0][3]))
        
        self.last_detected_needle = longest_line[0]
        return longest_line[0]
        
    def detect_needle_by_color(self, frame: np.ndarray, 
                              gauge_center: Tuple[int, int], 
                              gauge_radius: int) -> Optional[np.ndarray]:
        """
        Detect needle using color segmentation (Red).
        More stable than line detection for colored needles.
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Red color has two ranges in HSV (wrap around 180/0)
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Focus only on the gauge area (circle mask)
        circle_mask = np.zeros(mask.shape, dtype=np.uint8)
        cv2.circle(circle_mask, gauge_center, int(gauge_radius * 0.95), 255, -1)
        mask = cv2.bitwise_and(mask, circle_mask)
        
        # Remove small noise
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours of the red blob
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Select the largest contour (the needle)
        largest_contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(largest_contour) < 50: # Minimum size
            return None
            
        # Calculate the moments to find the centroid
        M = cv2.moments(largest_contour)
        if M["m00"] == 0:
            return None
            
        # Find the point in the contour furthest from the gauge center (the tip)
        max_dist = -1
        tip_x, tip_y = cX, cY
        
        for point in largest_contour:
            px, py = point[0]
            dist = math.sqrt((px - center_x)**2 + (py - center_y)**2)
            if dist > max_dist:
                max_dist = dist
                tip_x, tip_y = px, py
        
        # Construct a line from center to tip
        dx = tip_x - center_x
        dy = tip_y - center_y
        
        # Scale to gauge radius
        length = math.sqrt(dx**2 + dy**2)
        if length == 0: return None
        
        target_length = gauge_radius * 0.85
        x2 = int(center_x + dx * (target_length / length))
        y2 = int(center_y + dy * (target_length / length))
        
        line = np.array([center_x, center_y, x2, y2])
        self.last_detected_needle = line
        return line
    
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
        
        # Detect needle - Try Color first, fallback to Lines
        needle_line = self.detect_needle_by_color(frame, (center_x, center_y), radius)
        
        if needle_line is None:
            # Fallback to line detection if color fails
            needle_line = self.detect_needle_line(frame, (center_x, center_y), radius)
            
        if needle_line is None:
            return results
        
        results['needle_line'] = needle_line
        
        # Calculate angle
        raw_angle = self.calculate_needle_angle(needle_line, (center_x, center_y))
        
        # 1. Median Filter (Rolling Window)
        self.angle_window.append(raw_angle)
        
        # Sort angles for median calculation, handling the 0/360 wrap-around
        sorted_angles = sorted(list(self.angle_window))
        # Simple median for now, works if not near wrap-around
        median_angle = sorted_angles[len(sorted_angles)//2]
        
        # 2. Exponential Smoothing
        angle = median_angle
        if self.last_angle is not None:
            # Handle angle wrap-around (e.g. 359 to 1)
            diff = angle - self.last_angle
            if diff > 180: angle -= 360
            elif diff < -180: angle += 360
            
            angle = smooth_value(angle, self.last_angle, self.smoothing_alpha)
            angle = normalize_angle(angle)
            
        results['angle_degrees'] = angle
        self.last_angle = angle
        
        # Convert to pressure if config available
        if self.config and self.config.validate():
            from .utils import convert_angle_to_pressure
            
            min_angle = self.config.get('min_angle')
            max_angle = self.config.get('max_angle')
            min_pressure = self.config.get('min_pressure')
            max_pressure = self.config.get('max_pressure')
            
            pressure = convert_angle_to_pressure(angle, min_angle, max_angle, min_pressure, max_pressure)
            
            # Smoothing pressure
            if self.last_pressure is not None:
                pressure = smooth_value(pressure, self.last_pressure, self.smoothing_alpha)
            
            results['pressure'] = pressure
            self.last_pressure = pressure
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
