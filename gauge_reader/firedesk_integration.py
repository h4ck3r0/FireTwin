"""
FireDesk Integration Example
Demonstrates how to integrate gauge reader with the FireDesk dashboard.
"""

import json
import socket
import sys
import os
import time
import requests
import cv2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gauge_detector import GaugeDetector
from src.config_manager import CalibrationConfig

class FireDeskGaugeIntegration:
    def __init__(self, firedesk_host='localhost', firedesk_port=5000, server_url=None):
        self.firedesk_host = firedesk_host
        self.firedesk_port = firedesk_port
        self.server_url = server_url
        self.socket = None
        self.connected = False
    
    def connect_udp(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.connected = True
            return True
        except Exception as e:
            print(f"Error creating UDP socket: {e}")
            return False
    
    def push_to_cloud(self, pressure, unit, gauge_name):
        """Send gauge data to the Railway server."""
        if not self.server_url:
            return
        try:
            requests.post(f"{self.server_url}/api/update-gauge", json={
                "pressure": pressure,
                "unit": unit,
                "gauge_name": gauge_name,
                "timestamp": time.time()
            }, timeout=1)
        except:
            pass # Silently fail if cloud is unreachable

    def update_json_file(self, filepath, pressure, unit, gauge_name, angle_degrees):
        try:
            data = {
                'pressure': pressure,
                'unit': unit,
                'gauge_name': gauge_name,
                'angle_degrees': angle_degrees,
                'detection_success': True,
                'timestamp': time.time()
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error updating JSON file: {e}")

def run_gauge_reader_with_firedesk_integration(calibration_path: str = None):
    print("\n" + "=" * 70)
    print("GAUGE READER: REMOTE CLOUD SYNC MODE")
    print("=" * 70)
    
    # 1. Load Shared Config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'shared_config.json')
    try:
        with open(config_path, 'r') as f:
            shared = json.load(f)
            camera_source = shared.get('camera_url', 0)
            server_url = shared.get('firedesk_server_url')
    except:
        print("Warning: shared_config.json not found. Using defaults.")
        camera_source = 0
        server_url = None

    # 2. Setup paths
    status_file = os.path.join(os.path.dirname(__file__), 'gauge_status.json')
    public_status_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'gauge_status.json')
    
    # 3. Initialize
    calibration_path = calibration_path or os.path.join(os.path.dirname(__file__), 'calibrations/default_psi.json')
    config = CalibrationConfig(calibration_path)
    detector = GaugeDetector(config)
    firedesk = FireDeskGaugeIntegration(server_url=server_url)

    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print(f"ERROR: Cannot connect to camera: {camera_source}")
        return
    
    print(f"CONNECTED TO CAMERA: {camera_source}")
    print(f"REMOTE SYNC: {'ENABLED' if server_url else 'DISABLED'}")
    
    # 4. Create frames directory if it doesn't exist
    public_frames_dir = os.path.join(os.path.dirname(__file__), '..', 'public', 'frames')
    os.makedirs(public_frames_dir, exist_ok=True)
    live_frame_path = os.path.join(public_frames_dir, 'current_frame.jpg')

    try:
        print("PURE STREAMING MODE (No Detection, No Disk Writes)")
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            # Show local preview for debugging (optional)
            cv2.imshow('FireDesk Pure Stream', frame)
            
            # Note: Browser handles the direct MJPEG stream from the IP camera URL
            
            if cv2.waitKey(1) & 0xFF == ord('q'): break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_gauge_reader_with_firedesk_integration()
