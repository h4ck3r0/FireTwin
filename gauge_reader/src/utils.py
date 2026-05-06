"""
Utility functions for gauge reader system.
Provides helper functions for angle calculations, conversions, and FPS tracking.
"""

import math
import time
from collections import deque


class FPSCounter:
    """
    Real-time FPS counter with rolling average.
    Provides smooth FPS display without fluctuation.
    """
    
    def __init__(self, window_size=30):
        """
        Initialize FPS counter.
        
        Args:
            window_size (int): Number of frames for rolling average
        """
        self.window_size = window_size
        self.timestamps = deque(maxlen=window_size)
        self.start_time = time.time()
    
    def update(self):
        """Update FPS counter - call once per frame."""
        self.timestamps.append(time.time())
    
    def get_fps(self):
        """
        Calculate current FPS.
        
        Returns:
            float: Current frames per second
        """
        if len(self.timestamps) < 2:
            return 0
        
        time_diff = self.timestamps[-1] - self.timestamps[0]
        if time_diff == 0:
            return 0
        
        return len(self.timestamps) / time_diff


def calculate_angle_from_line(line, center_x, center_y):
    """
    Calculate angle of a line relative to gauge center.
    
    The angle is measured from the horizontal (3 o'clock position),
    going counterclockwise. Range: 0-360 degrees.
    
    Args:
        line: Detected line from HoughLinesP (x1, y1, x2, y2)
        center_x (float): X-coordinate of gauge center
        center_y (float): Y-coordinate of gauge center
    
    Returns:
        float: Angle in degrees (0-360)
    """
    x1, y1, x2, y2 = line[0]
    
    # Calculate vector from line endpoint to center
    # Use the point closer to center as reference
    dist1 = math.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
    dist2 = math.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)
    
    if dist1 < dist2:
        px, py = x1, y1
    else:
        px, py = x2, y2
    
    # Calculate angle using atan2
    # atan2(dy, dx) returns angle in radians from -π to π
    angle_rad = math.atan2(-(py - center_y), px - center_x)
    
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    
    # Normalize to 0-360 range
    if angle_deg < 0:
        angle_deg += 360
    
    return angle_deg


def convert_angle_to_pressure(angle, min_angle, max_angle, min_pressure, max_pressure):
    """
    Convert needle angle to pressure value using calibration parameters.
    
    Formula: Pressure = ((angle - min_angle) / (max_angle - min_angle)) * 
                       (max_pressure - min_pressure) + min_pressure
    
    Args:
        angle (float): Needle angle in degrees
        min_angle (float): Angle at minimum pressure (degrees)
        max_angle (float): Angle at maximum pressure (degrees)
        min_pressure (float): Minimum pressure value
        max_pressure (float): Maximum pressure value
    
    Returns:
        float: Calculated pressure value, clamped to [min_pressure, max_pressure]
    """
    # Clamp angle to valid range
    angle = max(min_angle, min(angle, max_angle))
    
    # Apply linear interpolation formula
    angle_range = max_angle - min_angle
    pressure_range = max_pressure - min_pressure
    
    if angle_range == 0:
        return min_pressure
    
    pressure = ((angle - min_angle) / angle_range) * pressure_range + min_pressure
    
    # Ensure pressure is within valid range
    pressure = max(min_pressure, min(pressure, max_pressure))
    
    return pressure


def normalize_angle(angle):
    """
    Normalize angle to 0-360 degree range.
    
    Args:
        angle (float): Angle in degrees
    
    Returns:
        float: Normalized angle (0-360)
    """
    angle = angle % 360
    if angle < 0:
        angle += 360
    return angle


def angle_difference(angle1, angle2):
    """
    Calculate shortest angular difference between two angles.
    
    Args:
        angle1 (float): First angle in degrees
        angle2 (float): Second angle in degrees
    
    Returns:
        float: Shortest angular difference in degrees (-180 to 180)
    """
    diff = normalize_angle(angle1 - angle2)
    if diff > 180:
        diff = 360 - diff
    return diff


def point_to_line_distance(px, py, x1, y1, x2, y2):
    """
    Calculate perpendicular distance from point to line.
    
    Uses the point-to-line distance formula:
    distance = |ax + by + c| / sqrt(a^2 + b^2)
    
    Args:
        px, py (float): Point coordinates
        x1, y1, x2, y2 (float): Line endpoint coordinates
    
    Returns:
        float: Perpendicular distance
    """
    numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
    denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    
    if denominator == 0:
        return 0
    
    return numerator / denominator


def line_length(x1, y1, x2, y2):
    """
    Calculate Euclidean distance between two points.
    
    Args:
        x1, y1, x2, y2 (float): Endpoint coordinates
    
    Returns:
        float: Distance between points
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def smooth_value(current_value, previous_value, alpha=0.7):
    """
    Apply exponential moving average smoothing.
    
    Reduces jitter in measurements while preserving responsiveness.
    
    Args:
        current_value (float): New measurement
        previous_value (float): Previous smoothed value
        alpha (float): Smoothing factor (0-1). Higher = more responsive
    
    Returns:
        float: Smoothed value
    """
    if previous_value is None:
        return current_value
    
    return alpha * current_value + (1 - alpha) * previous_value


def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * math.pi / 180


def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * 180 / math.pi
