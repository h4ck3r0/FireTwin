import math
import time
from collections import deque
class FPSCounter:
    
    def __init__(self, window_size=30):
        
        self.window_size = window_size
        self.timestamps = deque(maxlen=window_size)
        self.start_time = time.time()
    def update(self):
        """Update FPS counter - call once per frame."""
        self.timestamps.append(time.time())
    def get_fps(self):
        
        if len(self.timestamps) < 2:
            return 0
        time_diff = self.timestamps[-1] - self.timestamps[0]
        if time_diff == 0:
            return 0
        return len(self.timestamps) / time_diff
def calculate_angle_from_line(line, center_x, center_y):
    
    x1, y1, x2, y2 = line[0]
    dist1 = math.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
    dist2 = math.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)
    if dist1 > dist2:
        px, py = x1, y1
    else:
        px, py = x2, y2
    angle_rad = math.atan2(py - center_y, px - center_x)
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg
def convert_angle_to_pressure(angle, min_angle, max_angle, min_pressure, max_pressure):
    
    angle = normalize_angle(angle)
    min_angle = normalize_angle(min_angle)
    max_angle = normalize_angle(max_angle)
    sweep = normalize_angle(max_angle - min_angle)
    if sweep == 0:
        return min_pressure
    rel_angle = normalize_angle(angle - min_angle)
    if rel_angle > sweep:
        if rel_angle > (sweep + (360 - sweep) / 2):
            rel_angle = 0
        else:
            rel_angle = sweep
    pressure_range = max_pressure - min_pressure
    pressure = (rel_angle / sweep) * pressure_range + min_pressure
    return pressure
def normalize_angle(angle):
   
    angle = angle % 360
    if angle < 0:
        angle += 360
    return angle
def angle_difference(angle1, angle2):
    
    diff = normalize_angle(angle1 - angle2)
    if diff > 180:
        diff = 360 - diff
    return diff
def circular_median(angles):
    
    if not angles:
        return 0
    if len(angles) == 1:
        return angles[0]
    ref = angles[0]
    unwrapped = []
    for a in angles:
        diff = a - ref
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        unwrapped.append(ref + diff)
    unwrapped.sort()
    n = len(unwrapped)
    if n % 2 == 1:
        median = unwrapped[n // 2]
    else:
        median = (unwrapped[n // 2 - 1] + unwrapped[n // 2]) / 2
    return normalize_angle(median)
def point_to_line_distance(px, py, x1, y1, x2, y2):
    
    numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
    denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    if denominator == 0:
        return 0
    return numerator / denominator
def line_length(x1, y1, x2, y2):
    
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
def smooth_value(current_value, previous_value, alpha=0.7):
    if previous_value is None:
        return current_value
    return alpha * current_value + (1 - alpha) * previous_value
def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * math.pi / 180
def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * 180 / math.pi
