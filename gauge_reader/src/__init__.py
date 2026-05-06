"""
Package initialization for gauge reader modules.
"""

from .config_manager import CalibrationConfig, create_default_calibrations
from .gauge_detector import GaugeDetector
from .calibrator import GaugeCalibrator
from .utils import (
    FPSCounter,
    calculate_angle_from_line,
    convert_angle_to_pressure,
    smooth_value
)

__all__ = [
    'CalibrationConfig',
    'GaugeDetector',
    'GaugeCalibrator',
    'FPSCounter',
    'calculate_angle_from_line',
    'convert_angle_to_pressure',
    'smooth_value',
    'create_default_calibrations'
]
