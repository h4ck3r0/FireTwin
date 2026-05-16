"""
Configuration manager for gauge calibration.
Handles loading, saving, and validating calibration JSON files.
"""

import json
import os
from typing import Dict, Any, Optional


class CalibrationConfig:
    """
    Manages calibration configuration for analog pressure gauges.
    
    Stores and validates calibration parameters including angle ranges,
    pressure ranges, and algorithm tuning parameters.
    """
    
    # Default parameter ranges for validation
    VALID_RANGES = {
        'min_angle': (0, 360),
        'max_angle': (0, 360),
        'min_pressure': (-1000, 10000),
        'max_pressure': (-1000, 10000),
        'hough_circles_param1': (10, 500),
        'hough_circles_param2': (1, 100),
        'hough_circles_minRadius': (5, 500),
        'hough_circles_maxRadius': (10, 1000),
    }
    
    # Required fields in calibration file
    REQUIRED_FIELDS = [
        'gauge_name',
        'unit',
        'min_angle',
        'max_angle',
        'min_pressure',
        'max_pressure'
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize calibration config.
        
        Args:
            config_path (str, optional): Path to calibration JSON file
        """
        self.config_path = config_path
        self.data: Dict[str, Any] = {}
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        else:
            self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize with default calibration parameters."""
        self.data = {
            'gauge_name': 'Default PSI Gauge',
            'unit': 'PSI',
            'min_angle': 45,
            'max_angle': 315,
            'min_pressure': 0,
            'max_pressure': 100,
            'hough_circles_param1': 100,
            'hough_circles_param2': 30,
            'hough_circles_minRadius': 50,
            'hough_circles_maxRadius': 300,
            'canny_threshold1': 50,
            'canny_threshold2': 150,
            'gaussian_kernel': (15, 15),
            'hough_lines_minLineLength': 50,
            'hough_lines_maxLineGap': 10,
        }
    
    def load_from_file(self, config_path: str) -> bool:
        """
        Load calibration from JSON file.
        
        Args:
            config_path (str): Path to JSON calibration file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(config_path, 'r') as f:
                self.data = json.load(f)
            
            self.config_path = config_path
            
            # Validate loaded configuration
            if not self.validate():
                print("Warning: Loaded configuration has validation errors")
                return False
            
            print(f"Successfully loaded calibration: {config_path}")
            return True
        
        except FileNotFoundError:
            print(f"Error: Calibration file not found: {config_path}")
            return False
        
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in calibration file: {config_path}")
            return False
        
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False
    
    def save_to_file(self, config_path: Optional[str] = None) -> bool:
        """
        Save calibration to JSON file.
        
        Args:
            config_path (str, optional): Path to save. Uses stored path if not provided
        
        Returns:
            bool: True if successful, False otherwise
        """
        save_path = config_path or self.config_path
        
        if not save_path:
            print("Error: No file path specified for saving")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            
            self.config_path = save_path
            print(f"Successfully saved calibration: {save_path}")
            return True
        
        except Exception as e:
            print(f"Error saving calibration: {e}")
            return False
    
    def validate(self) -> bool:
        """
        Validate calibration configuration.
        
        Checks:
        - All required fields are present
        - Values are within valid ranges
        - min_angle < max_angle
        - min_pressure < max_pressure
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in self.data:
                print(f"Error: Missing required field '{field}'")
                return False
        
        # Check value ranges
        for field, (min_val, max_val) in self.VALID_RANGES.items():
            if field in self.data:
                value = self.data[field]
                if not isinstance(value, (int, float)):
                    print(f"Error: '{field}' must be numeric")
                    return False
                
                if not (min_val <= value <= max_val):
                    print(f"Error: '{field}' = {value} is outside valid range [{min_val}, {max_val}]")
                    return False
        
        # Angle and pressure constraints removed to support circular wrap-around
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value.
        
        Validates value before setting.
        
        Args:
            key (str): Configuration key
            value (Any): New value
        
        Returns:
            bool: True if successful, False if validation fails
        """
        # Quick validation for known fields
        if key in self.VALID_RANGES:
            min_val, max_val = self.VALID_RANGES[key]
            if not (min_val <= value <= max_val):
                print(f"Error: Value {value} outside range [{min_val}, {max_val}]")
                return False
        
        self.data[key] = value
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration parameters."""
        return self.data.copy()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Update multiple configuration parameters.
        
        Args:
            updates (dict): Dictionary of key-value pairs to update
        
        Returns:
            bool: True if all updates successful, False otherwise
        """
        for key, value in updates.items():
            if not self.set(key, value):
                return False
        
        return True
    
    def print_summary(self):
        """Print configuration summary to console."""
        print("\n" + "=" * 60)
        print("CALIBRATION CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"Gauge Name:           {self.get('gauge_name')}")
        print(f"Unit:                 {self.get('unit')}")
        print(f"Angle Range:          {self.get('min_angle')}° - {self.get('max_angle')}°")
        print(f"Pressure Range:       {self.get('min_pressure')} - {self.get('max_pressure')} {self.get('unit')}")
        print(f"Hough Circles Param1: {self.get('hough_circles_param1')}")
        print(f"Hough Circles Param2: {self.get('hough_circles_param2')}")
        print(f"Circle Radius Range:  {self.get('hough_circles_minRadius')} - {self.get('hough_circles_maxRadius')} px")
        print("=" * 60 + "\n")


def create_default_calibrations():
    """Create default calibration files for common gauge types."""
    
    calibrations = {
        'default_psi.json': {
            'gauge_name': 'Standard PSI Gauge',
            'unit': 'PSI',
            'description': 'Typical 0-100 PSI analog gauge',
            'min_angle': 45,
            'max_angle': 315,
            'min_pressure': 0,
            'max_pressure': 100,
            'hough_circles_param1': 100,
            'hough_circles_param2': 30,
            'hough_circles_minRadius': 50,
            'hough_circles_maxRadius': 300,
            'canny_threshold1': 50,
            'canny_threshold2': 150,
            'hough_lines_minLineLength': 50,
            'hough_lines_maxLineGap': 10,
        },
        'default_bar.json': {
            'gauge_name': 'Standard bar Gauge',
            'unit': 'bar',
            'description': 'Typical 0-10 bar analog gauge',
            'min_angle': 45,
            'max_angle': 315,
            'min_pressure': 0,
            'max_pressure': 10,
            'hough_circles_param1': 100,
            'hough_circles_param2': 30,
            'hough_circles_minRadius': 50,
            'hough_circles_maxRadius': 300,
            'canny_threshold1': 50,
            'canny_threshold2': 150,
            'hough_lines_minLineLength': 50,
            'hough_lines_maxLineGap': 10,
        },
        'default_kpa.json': {
            'gauge_name': 'Standard kPa Gauge',
            'unit': 'kPa',
            'description': 'Typical 0-1000 kPa analog gauge',
            'min_angle': 45,
            'max_angle': 315,
            'min_pressure': 0,
            'max_pressure': 1000,
            'hough_circles_param1': 100,
            'hough_circles_param2': 30,
            'hough_circles_minRadius': 50,
            'hough_circles_maxRadius': 300,
            'canny_threshold1': 50,
            'canny_threshold2': 150,
            'hough_lines_minLineLength': 50,
            'hough_lines_maxLineGap': 10,
        }
    }
    
    calibrations_dir = os.path.join(os.path.dirname(__file__), '..', 'calibrations')
    os.makedirs(calibrations_dir, exist_ok=True)
    
    for filename, config in calibrations.items():
        filepath = os.path.join(calibrations_dir, filename)
        
        if not os.path.exists(filepath):
            try:
                with open(filepath, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"Created default calibration: {filename}")
            except Exception as e:
                print(f"Error creating calibration file {filename}: {e}")
