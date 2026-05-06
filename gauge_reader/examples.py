"""
Advanced Examples & Use Cases
Demonstrates various ways to use the gauge reader system.
"""

import cv2
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gauge_detector import GaugeDetector
from config_manager import CalibrationConfig
from utils import smooth_value, FPSCounter


# ============================================================================
# EXAMPLE 1: Simple Batch Processing
# ============================================================================

def batch_process_images(image_dir: str, calibration_path: str):
    """
    Process multiple gauge images from a directory.
    
    Args:
        image_dir: Directory containing gauge images
        calibration_path: Path to calibration JSON
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Batch Processing Gauge Images")
    print("="*70)
    
    config = CalibrationConfig(calibration_path)
    detector = GaugeDetector(config)
    
    results_list = []
    
    for image_file in sorted(os.listdir(image_dir)):
        if not image_file.lower().endswith(('.jpg', '.png', '.jpeg')):
            continue
        
        image_path = os.path.join(image_dir, image_file)
        frame = cv2.imread(image_path)
        
        results = detector.process_frame(frame)
        
        print(f"{image_file:30s} | Pressure: {results['pressure']:6.1f} {results['pressure_unit']} | Angle: {results['angle_degrees']:6.1f}°")
        
        results_list.append({
            'image': image_file,
            'pressure': results['pressure'],
            'angle': results['angle_degrees'],
            'success': results['success']
        })
    
    print(f"\nProcessed {len(results_list)} images")
    return results_list


# ============================================================================
# EXAMPLE 2: Video File Processing with Output
# ============================================================================

def process_video_file(video_path: str, calibration_path: str, output_path: str = None):
    """
    Process video file and optionally save annotated output.
    
    Args:
        video_path: Path to input video
        calibration_path: Path to calibration JSON
        output_path: Path to save output video (optional)
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Video File Processing")
    print("="*70)
    
    config = CalibrationConfig(calibration_path)
    detector = GaugeDetector(config)
    fps_counter = FPSCounter()
    
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video: {video_path}")
    print(f"Frames: {frame_count}, FPS: {fps}, Resolution: {width}×{height}")
    
    # Setup output video writer if requested
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    pressures = []
    angles = []
    frame_num = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_num += 1
        
        # Process frame
        results = detector.process_frame(frame)
        
        # Annotate frame
        frame = detector.draw_detection_results(frame, results)
        
        # Add frame number
        cv2.putText(frame, f"Frame: {frame_num}/{frame_count}", 
                   (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (0, 255, 0), 2)
        
        if results['success']:
            pressures.append(results['pressure'])
            angles.append(results['angle_degrees'])
        
        # Write output
        if writer:
            writer.write(frame)
        
        fps_counter.update()
        
        # Print progress
        if frame_num % 30 == 0:
            print(f"Processing: {frame_num}/{frame_count} frames ({frame_num/frame_count*100:.1f}%)")
    
    cap.release()
    if writer:
        writer.release()
        print(f"Output saved: {output_path}")
    
    # Print statistics
    if pressures:
        print(f"\nStatistics:")
        print(f"  Avg Pressure:     {np.mean(pressures):.2f} {config.get('unit')}")
        print(f"  Min Pressure:     {np.min(pressures):.2f} {config.get('unit')}")
        print(f"  Max Pressure:     {np.max(pressures):.2f} {config.get('unit')}")
        print(f"  Std Deviation:    {np.std(pressures):.2f}")
        print(f"  Avg Angle:        {np.mean(angles):.2f}°")


# ============================================================================
# EXAMPLE 3: Real-Time Smoothed Readings
# ============================================================================

def smoothed_realtime_reading(calibration_path: str, smoothing_factor: float = 0.7):
    """
    Real-time gauge reading with exponential moving average smoothing.
    
    Args:
        calibration_path: Path to calibration JSON
        smoothing_factor: Smoothing factor (0-1, higher = less smoothing)
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Smoothed Real-Time Reading")
    print("="*70)
    
    config = CalibrationConfig(calibration_path)
    detector = GaugeDetector(config)
    fps_counter = FPSCounter()
    
    last_pressure = None
    detection_count = 0
    total_frames = 0
    
    cap = cv2.VideoCapture(0)
    
    print(f"Smoothing Factor: {smoothing_factor}")
    print(f"(Higher = more responsive, Lower = smoother)")
    print(f"\nPress 'q' to quit\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            total_frames += 1
            
            # Process frame
            results = detector.process_frame(frame)
            
            # Apply smoothing
            if results['success'] and results['pressure'] is not None:
                pressure = smooth_value(results['pressure'], last_pressure, 
                                       alpha=smoothing_factor)
                last_pressure = pressure
                detection_count += 1
                
                # Update results
                results['pressure'] = pressure
            
            # Draw
            frame = detector.draw_detection_results(frame, results)
            
            # Draw smoothing info
            h, w = frame.shape[:2]
            info_text = f"Smoothing: {smoothing_factor:.1f} | Raw: {results['pressure']:.1f} | Smoothed: {last_pressure:.1f}"
            cv2.putText(frame, info_text, (10, h - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            
            # Display
            fps_counter.update()
            cv2.imshow('Smoothed Real-Time Reading', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\nStatistics:")
        print(f"  Total Frames:     {total_frames}")
        print(f"  Detections:       {detection_count}")
        print(f"  Detection Rate:   {detection_count/total_frames*100:.1f}%")


# ============================================================================
# EXAMPLE 4: Pressure Range Monitoring
# ============================================================================

def monitor_pressure_range(calibration_path: str, warn_low: float = 20, warn_high: float = 80):
    """
    Monitor pressure and alert when out of normal range.
    
    Args:
        calibration_path: Path to calibration JSON
        warn_low: Low pressure threshold
        warn_high: High pressure threshold
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Pressure Range Monitoring")
    print("="*70)
    
    config = CalibrationConfig(calibration_path)
    detector = GaugeDetector(config)
    
    cap = cv2.VideoCapture(0)
    
    print(f"Monitoring: {config.get('gauge_name')}")
    print(f"Normal Range: {warn_low} - {warn_high} {config.get('unit')}")
    print(f"Press 'q' to quit\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            results = detector.process_frame(frame)
            frame = detector.draw_detection_results(frame, results)
            
            h, w = frame.shape[:2]
            
            if results['success'] and results['pressure'] is not None:
                pressure = results['pressure']
                
                # Determine status
                if pressure < warn_low:
                    status = "⚠️ LOW"
                    color = (0, 0, 255)
                elif pressure > warn_high:
                    status = "⚠️ HIGH"
                    color = (0, 0, 255)
                else:
                    status = "✓ NORMAL"
                    color = (0, 255, 0)
                
                # Draw status
                status_text = f"{status}: {pressure:.1f} {config.get('unit')}"
                cv2.putText(frame, status_text, (10, h - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            
            cv2.imshow('Pressure Monitoring', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()


# ============================================================================
# EXAMPLE 5: Multi-Calibration Comparison
# ============================================================================

def compare_calibrations(frame_path: str, calibration_paths: dict):
    """
    Compare readings from same frame using different calibrations.
    
    Args:
        frame_path: Path to test gauge image
        calibration_paths: Dict of {name: calibration_path}
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Multi-Calibration Comparison")
    print("="*70)
    
    frame = cv2.imread(frame_path)
    h, w = frame.shape[:2]
    
    results_list = []
    
    for name, calib_path in calibration_paths.items():
        config = CalibrationConfig(calib_path)
        detector = GaugeDetector(config)
        
        results = detector.process_frame(frame)
        results_list.append({
            'name': name,
            'config': config,
            'results': results
        })
        
        print(f"{name:25s} | Pressure: {results['pressure']:8.2f} | Angle: {results['angle_degrees']:7.2f}°")
    
    # Show frame with multiple calibrations
    canvas = frame.copy()
    y_offset = 30
    
    for item in results_list:
        text = f"{item['name']}: {item['results']['pressure']:.2f} {item['config'].get('unit')}"
        cv2.putText(canvas, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_offset += 35
    
    cv2.imshow('Calibration Comparison', canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ============================================================================
# EXAMPLE 6: Angle-Only Mode (No Pressure Conversion)
# ============================================================================

def angle_only_mode(device_id: int = 0):
    """
    Display only needle angle without pressure conversion.
    Useful for debugging angle detection.
    
    Args:
        device_id: Camera device ID
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Angle-Only Detection Mode")
    print("="*70)
    
    # Create detector without config
    detector = GaugeDetector(config=None)
    
    cap = cv2.VideoCapture(device_id)
    
    print("Displaying needle angle only (no pressure conversion)")
    print("Press 'q' to quit\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect gauge
            gauge_info = detector.detect_gauge_circle(frame)
            if gauge_info is None:
                cv2.imshow('Angle Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            cx, cy, r = gauge_info
            
            # Detect needle
            needle_line = detector.detect_needle_line(frame, (cx, cy), r)
            if needle_line is None:
                cv2.circle(frame, (cx, cy), r, (255, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.imshow('Angle Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            # Calculate angle
            angle = detector.calculate_needle_angle(needle_line, (cx, cy))
            
            # Draw
            cv2.circle(frame, (cx, cy), r, (255, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            x1, y1, x2, y2 = needle_line
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            # Display angle
            angle_text = f"Angle: {angle:.1f}°"
            cv2.putText(frame, angle_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Angle Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("GAUGE READER ADVANCED EXAMPLES")
    print("="*70)
    print("\nAvailable examples:")
    print("  1. Batch image processing")
    print("  2. Video file processing")
    print("  3. Smoothed real-time reading")
    print("  4. Pressure range monitoring")
    print("  5. Multi-calibration comparison")
    print("  6. Angle-only detection mode")
    print("\nRun directly or import functions for custom usage")
