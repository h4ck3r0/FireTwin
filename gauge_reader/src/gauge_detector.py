import cv2
import numpy as np
import math
from typing import Tuple, Optional, List
try:
    from .utils import (calculate_angle_from_line, line_length, point_to_line_distance,
                        smooth_value, normalize_angle, convert_angle_to_pressure,
                        circular_median, angle_difference)
except ImportError:
    from utils import (calculate_angle_from_line, line_length, point_to_line_distance,
                       smooth_value, normalize_angle, convert_angle_to_pressure,
                       circular_median, angle_difference)
from collections import deque
class GaugeDetector:
    
    def __init__(self, config=None):
       
        self.config = config
        self.last_detected_circle = None
        self.last_detected_needle = None
        self.last_angle = None
        self.last_pressure = None
        self.circle_lock_frames = 0
        self.max_circle_lock = 30  
        self.smoothing_alpha = 0.25  
        self.circle_jump_threshold = 15  
        self.angle_window = deque(maxlen=9)  
        self.needle_lock_frames = 0
        self.max_needle_lock = 5  
        self.outlier_threshold_degrees = 25  
    def detect_gauge_circle(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        blur_kernel = self.config.get('gaussian_kernel', (15, 15)) if self.config else (15, 15)
        if isinstance(blur_kernel, list):
            blur_kernel = tuple(blur_kernel)
        blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
        if self.config:
            param1 = self.config.get('hough_circles_param1', 100)
            param2 = self.config.get('hough_circles_param2', 30)
            min_radius = self.config.get('hough_circles_minRadius', 50)
            max_radius = self.config.get('hough_circles_maxRadius', 300)
        else:
            param1, param2 = 100, 30
            min_radius, max_radius = 50, 300
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
            if self.last_detected_circle and self.circle_lock_frames < self.max_circle_lock:
                self.circle_lock_frames += 1
                return self.last_detected_circle
            return None
        circles = np.uint16(np.around(circles))
        circle = circles[0][0]
        center_x, center_y, radius = int(circle[0]), int(circle[1]), int(circle[2])
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
        
        center_x, center_y = gauge_center
        h, w = frame.shape[:2]
        margin = int(gauge_radius * 0.1)
        x1_roi = max(0, center_x - gauge_radius - margin)
        y1_roi = max(0, center_y - gauge_radius - margin)
        x2_roi = min(w, center_x + gauge_radius + margin)
        y2_roi = min(h, center_y + gauge_radius + margin)
        roi = frame[y1_roi:y2_roi, x1_roi:x2_roi]
        roi_cx = center_x - x1_roi
        roi_cy = center_y - y1_roi
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        circle_mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(circle_mask, (roi_cx, roi_cy), int(gauge_radius * 0.95), 255, -1)
        gray = cv2.bitwise_and(gray, circle_mask)
        canny_threshold1 = self.config.get('canny_threshold1', 40) if self.config else 40
        canny_threshold2 = self.config.get('canny_threshold2', 120) if self.config else 120
        edges = cv2.Canny(gray, canny_threshold1, canny_threshold2)
        if self.config:
            min_line_length = self.config.get('hough_lines_minLineLength', 50)
            max_line_gap = self.config.get('hough_lines_maxLineGap', 10)
        else:
            min_line_length, max_line_gap = 50, 10
        dynamic_min_length = max(min_line_length, int(gauge_radius * 0.35))
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=40,
            minLineLength=dynamic_min_length,
            maxLineGap=max_line_gap
        )
        if lines is None or len(lines) == 0:
            if self.last_detected_needle is not None and self.needle_lock_frames < self.max_needle_lock:
                self.needle_lock_frames += 1
                return self.last_detected_needle
            return None
        scored_lines = []
        for line in lines:
            lx1, ly1, lx2, ly2 = line[0]
            length = line_length(lx1, ly1, lx2, ly2)
            if length < dynamic_min_length:
                continue
            dist_to_center = point_to_line_distance(roi_cx, roi_cy, lx1, ly1, lx2, ly2)
            if dist_to_center < gauge_radius * 0.20:
                length_score = length / gauge_radius  
                proximity_score = 1.0 - (dist_to_center / (gauge_radius * 0.20))
                d1 = math.sqrt((lx1 - roi_cx)**2 + (ly1 - roi_cy)**2)
                d2 = math.sqrt((lx2 - roi_cx)**2 + (ly2 - roi_cy)**2)
                center_proximity = min(d1, d2) / gauge_radius
                center_score = max(0, 1.0 - center_proximity)  
                total_score = length_score * 0.4 + proximity_score * 0.3 + center_score * 0.3
                frame_line = np.array([[lx1 + x1_roi, ly1 + y1_roi, lx2 + x1_roi, ly2 + y1_roi]])
                scored_lines.append((total_score, frame_line))
        if not scored_lines:
            if self.last_detected_needle is not None and self.needle_lock_frames < self.max_needle_lock:
                self.needle_lock_frames += 1
                return self.last_detected_needle
            return None
        best_line = max(scored_lines, key=lambda x: x[0])[1]
        self.last_detected_needle = best_line[0]
        self.needle_lock_frames = 0
        return best_line[0]
    def detect_needle_by_color(self, frame: np.ndarray, 
                              gauge_center: Tuple[int, int], 
                              gauge_radius: int) -> Optional[np.ndarray]:
       
        cx, cy = gauge_center
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 40, 30])
        upper_red1 = np.array([15, 255, 255])
        lower_red2 = np.array([160, 40, 30])
        upper_red2 = np.array([180, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        circle_mask = np.zeros(mask.shape, dtype=np.uint8)
        cv2.circle(circle_mask, (cx, cy), int(gauge_radius * 0.90), 255, -1)
        pivot_exclusion_r = max(10, int(gauge_radius * 0.40))
        cv2.circle(circle_mask, (cx, cy), pivot_exclusion_r, 0, -1)
        mask = cv2.bitwise_and(mask, circle_mask)
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        valid_contours = [c for c in contours if cv2.contourArea(c) > 80]
        if not valid_contours:
            return None
        largest_contour = max(valid_contours, key=cv2.contourArea)
        max_dist = -1
        tip_x, tip_y = cx, cy
        for point in largest_contour:
            px, py = point[0]
            dist = math.sqrt((px - cx)**2 + (py - cy)**2)
            if dist > max_dist:
                max_dist = dist
                tip_x, tip_y = px, py
        if max_dist < gauge_radius * 0.20:
            return None
        dx = tip_x - cx
        dy = tip_y - cy
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            return None
        target_length = gauge_radius * 0.85
        x2 = int(cx + dx * (target_length / length))
        y2 = int(cy + dy * (target_length / length))
        line = np.array([cx, cy, x2, y2])
        self.last_detected_needle = line
        self.needle_lock_frames = 0
        return line
    def calculate_needle_angle(self, needle_line: np.ndarray, 
                              gauge_center: Tuple[int, int]) -> float:
       
        line_reshaped = np.array([needle_line])
        angle = calculate_angle_from_line(line_reshaped, gauge_center[0], gauge_center[1])
        return angle
    def process_frame(self, frame: np.ndarray) -> dict:
        
        results = {
            'success': False,
            'gauge_center': None,
            'gauge_radius': None,
            'needle_line': None,
            'angle_degrees': None,
            'pressure': None,
            'pressure_unit': None
        }
        gauge_info = self.detect_gauge_circle(frame)
        if gauge_info is None:
            return results
        center_x, center_y, radius = gauge_info
        results['gauge_center'] = (center_x, center_y)
        results['gauge_radius'] = radius
        needle_line = None
        try:
            needle_line = self.detect_needle_by_color(frame, (center_x, center_y), radius)
        except Exception:
            pass  
        if needle_line is None:
            needle_line = self.detect_needle_line(frame, (center_x, center_y), radius)
        if needle_line is None:
            return results
        results['needle_line'] = needle_line
        raw_angle = self.calculate_needle_angle(needle_line, (center_x, center_y))
        self.angle_window.append(raw_angle)
        median_angle = circular_median(list(self.angle_window))
        angle = median_angle
        if self.last_angle is not None:
            diff = angle - self.last_angle
            if diff > 180:
                angle -= 360
            elif diff < -180:
                angle += 360
            angle = smooth_value(angle, self.last_angle, self.smoothing_alpha)
            angle = normalize_angle(angle)
        results['angle_degrees'] = angle
        self.last_angle = angle
        if self.config and self.config.validate():
            min_angle = self.config.get('min_angle')
            max_angle = self.config.get('max_angle')
            min_pressure = self.config.get('min_pressure')
            max_pressure = self.config.get('max_pressure')
            pressure = convert_angle_to_pressure(angle, min_angle, max_angle, min_pressure, max_pressure)
            pressure = round(pressure, 1)
            results['pressure'] = pressure
            self.last_pressure = pressure
            results['pressure_unit'] = self.config.get('unit', 'PSI')
        results['success'] = True
        return results
    def draw_detection_results(self, frame: np.ndarray, results: dict, 
                              draw_circle: bool = True, 
                              draw_needle: bool = True,
                              draw_center: bool = True) -> np.ndarray:
       
        if not results['success']:
            return frame
        if draw_circle and results['gauge_center']:
            center_x, center_y = results['gauge_center']
            radius = results['gauge_radius']
            cv2.circle(frame, (center_x, center_y), radius, (255, 255, 0), 2)  
        if draw_center and results['gauge_center']:
            center_x, center_y = results['gauge_center']
            cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)  
        if draw_needle and results['needle_line'] is not None:
            x1, y1, x2, y2 = results['needle_line']
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  
        y_offset = 30
        if results['angle_degrees'] is not None:
            angle_text = f"Angle: {results['angle_degrees']:.1f}"
            cv2.putText(frame, angle_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            y_offset += 35
        if results['pressure'] is not None:
            pressure_text = f"Pressure: {results['pressure']:.1f} {results['pressure_unit']}"
            cv2.putText(frame, pressure_text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame
