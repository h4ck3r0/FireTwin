"""
FireDesk Integration Example
Demonstrates how to integrate gauge reader with the FireDesk dashboard.
"""

import json
import socket
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gauge_detector import GaugeDetector
from src.config_manager import CalibrationConfig
import cv2


class FireDeskGaugeIntegration:
    """
    Integration module for sending gauge readings to FireDesk dashboard.
    
    Supports multiple communication methods:
    1. UDP socket for real-time streaming
    2. JSON file updates for polling
    3. REST API (future)
    """
    
    def __init__(self, firedesk_host='localhost', firedesk_port=5000):
        """
        Initialize FireDesk integration.
        
        Args:
            firedesk_host (str): Host address of FireDesk server
            firedesk_port (int): Port number for communication
        """
        self.firedesk_host = firedesk_host
        self.firedesk_port = firedesk_port
        self.socket = None
        self.connected = False
    
    def connect_udp(self) -> bool:
        """
        Connect to FireDesk via UDP socket.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.connected = True
            print(f"UDP connection ready: {self.firedesk_host}:{self.firedesk_port}")
            return True
        except Exception as e:
            print(f"Error creating UDP socket: {e}")
            return False
    
    def send_gauge_reading_udp(self, pressure: float, unit: str, 
                               gauge_name: str = "Pump") -> bool:
        """
        Send gauge reading to FireDesk via UDP.
        
        Args:
            pressure (float): Measured pressure value
            unit (str): Pressure unit (PSI, bar, kPa)
            gauge_name (str): Name of gauge
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected or not self.socket:
            return False
        
        try:
            # Create message in JSON format
            message = {
                'type': 'gauge_reading',
                'gauge_name': gauge_name,
                'pressure': pressure,
                'unit': unit
            }
            
            # Send to FireDesk
            self.socket.sendto(
                json.dumps(message).encode(),
                (self.firedesk_host, self.firedesk_port)
            )
            return True
        except Exception as e:
            print(f"Error sending UDP message: {e}")
            return False
    
    def update_json_file(self, filepath: str, pressure: float, 
                        unit: str, gauge_name: str = "Pump"):
        """
        Update gauge reading via JSON file.
        Useful for inter-process communication.
        
        Args:
            filepath (str): Path to JSON status file
            pressure (float): Measured pressure value
            unit (str): Pressure unit
            gauge_name (str): Name of gauge
        """
        try:
            # Read existing data if file exists
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Update gauge reading
            data[gauge_name] = {
                'pressure': pressure,
                'unit': unit,
                'timestamp': __import__('time').time()
            }
            
            # Write back to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"Error updating JSON file: {e}")
    
    def close(self):
        """Close connection."""
        if self.socket:
            self.socket.close()
        self.connected = False


def run_gauge_reader_with_firedesk_integration(calibration_path: str = None):
    """
    Run gauge reader with real-time FireDesk integration.
    
    Args:
        calibration_path (str, optional): Path to calibration file
    """
    print("\n" + "=" * 70)
    print("GAUGE READER WITH FIREDESK INTEGRATION")
    print("=" * 70)
    
    # Load calibration
    calibration_path = calibration_path or os.path.join(
        os.path.dirname(__file__),
        'calibrations/default_psi.json'
    )
    
    config = CalibrationConfig(calibration_path)
    if not config.validate():
        print("ERROR: Invalid calibration")
        return
    
    # Initialize detector and integration
    detector = GaugeDetector(config)
    firedesk = FireDeskGaugeIntegration('localhost', 5000)
    
    if not firedesk.connect_udp():
        print("Warning: Could not connect to FireDesk (will try JSON file fallback)")
    
    # Status file for FireDesk polling
    status_file = os.path.join(os.path.dirname(__file__), 'gauge_status.json')
    
    # Also write to public folder for web dashboard access
    public_status_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'gauge_status.json')
    
    # Open video capture
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Cannot open video capture")
        return
    
    print(f"Streaming gauge readings to FireDesk...")
    print(f"Status file: {status_file}")
    print("Press 'q' to quit\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            results = detector.process_frame(frame)
            
            if results['success'] and results['pressure'] is not None:
                # Send to FireDesk via UDP
                firedesk.send_gauge_reading_udp(
                    results['pressure'],
                    results['pressure_unit'],
                    config.get('gauge_name')
                )
                
                # Update JSON file (local)
                firedesk.update_json_file(
                    status_file,
                    results['pressure'],
                    results['pressure_unit'],
                    config.get('gauge_name')
                )
                
                # Update JSON file (public folder for web dashboard)
                firedesk.update_json_file(
                    public_status_file,
                    results['pressure'],
                    results['pressure_unit'],
                    config.get('gauge_name')
                )
                
                # Print to console
                print(f"Pressure: {results['pressure']:.1f} {results['pressure_unit']} | Angle: {results['angle_degrees']:.1f}°")
            
            # Display frame
            annotated = detector.draw_detection_results(frame, results)
            cv2.imshow('Gauge Reader -> FireDesk', annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        firedesk.close()
        print("\nIntegration closed")


if __name__ == '__main__':
    run_gauge_reader_with_firedesk_integration()
