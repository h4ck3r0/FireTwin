import os
import cv2
import numpy as np
import base64
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from src.gauge_detector import GaugeDetector
from src.config_manager import CalibrationConfig
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
detectors: Dict[str, GaugeDetector] = {}
latest_state = {
    "pressure": 0.0,
    "unit": "PSI",
    "timestamp": 0
}
def get_detector(calibration_id: str) -> GaugeDetector:
    if calibration_id not in detectors:
        cal_path = os.path.join(os.path.dirname(__file__), 'calibrations', f"{calibration_id}.json")
        if not os.path.exists(cal_path):
            cal_path = os.path.join(os.path.dirname(__file__), 'calibrations', 'default_psi.json')
        config = CalibrationConfig(cal_path)
        detectors[calibration_id] = GaugeDetector(config)
    return detectors[calibration_id]
@app.websocket("/ws/gauge")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get('type') == 'frame':
                gauge_id = message.get('gauge_id', 'default_psi')
                image_data = message.get('image')
                if not image_data:
                    continue
                encoded_data = image_data.split(',')[1]
                nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is None:
                    continue
                try:
                    detector = get_detector(gauge_id)
                    results = detector.process_frame(frame)
                    response = {
                        'type': 'results',
                        'gauge_id': gauge_id,
                        'success': results['success'],
                        'pressure': results['pressure'],
                        'unit': results['pressure_unit'],
                        'angle': results['angle_degrees'],
                        'gauge_center': results['gauge_center'],
                        'gauge_radius': results['gauge_radius'],
                        'needle_line': results['needle_line'].tolist() if results['needle_line'] is not None else None
                    }
                    if results['success'] and results['pressure'] is not None:
                        latest_state["pressure"] = results['pressure']
                        latest_state["unit"] = results['pressure_unit']
                        latest_state["timestamp"] = asyncio.get_event_loop().time()
                    await websocket.send_text(json.dumps(response))
                except Exception as frame_err:
                    print(f"Error processing frame: {frame_err}")
                    await websocket.send_text(json.dumps({'type': 'error', 'message': str(frame_err)}))
            elif message.get('type') == 'start_ip_camera':
                gauge_id = message.get('gauge_id', 'default_psi')
                camera_url = message.get('camera_url')
                if not camera_url:
                    await websocket.send_text(json.dumps({'type': 'error', 'message': 'No camera_url provided'}))
                    continue
                print(f"Starting IP camera stream from {camera_url}")
                websocket.state.ip_camera_running = True
                async def stream_camera():
                    cap = cv2.VideoCapture(camera_url)
                    detector = get_detector(gauge_id)
                    try:
                        while getattr(websocket.state, 'ip_camera_running', False):
                            ret, frame = cap.read()
                            if not ret:
                                print("Failed to read from IP camera")
                                await asyncio.sleep(1)
                                continue
                            results = detector.process_frame(frame)
                            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                            _, buffer = cv2.imencode('.jpg', frame, encode_param)
                            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                            image_data = 'data:image/jpeg;base64,' + jpg_as_text
                            response = {
                                'type': 'stream_results',
                                'gauge_id': gauge_id,
                                'success': results['success'],
                                'pressure': results['pressure'],
                                'unit': results['pressure_unit'],
                                'angle': results['angle_degrees'],
                                'gauge_center': results['gauge_center'],
                                'gauge_radius': results['gauge_radius'],
                                'needle_line': results['needle_line'].tolist() if results['needle_line'] is not None else None,
                                'image': image_data
                            }
                            if results['success'] and results['pressure'] is not None:
                                latest_state["pressure"] = results['pressure']
                                latest_state["unit"] = results['pressure_unit']
                                latest_state["timestamp"] = asyncio.get_event_loop().time()
                            await websocket.send_text(json.dumps(response))
                            await asyncio.sleep(0.05)
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        print(f"IP Camera Stream Error: {e}")
                    finally:
                        cap.release()
                asyncio.create_task(stream_camera())
            elif message.get('type') == 'stop_ip_camera':
                websocket.state.ip_camera_running = False
                print("Stopped IP camera stream")
            elif message.get('type') == 'calibrate':
                gauge_id = message.get('gauge_id')
                cal_data = message.get('data')
                cal_path = os.path.join(os.path.dirname(__file__), 'calibrations', f"{gauge_id}.json")
                with open(cal_path, 'w') as f:
                    json.dump(cal_data, f, indent=2)
                if gauge_id in detectors:
                    del detectors[gauge_id]
                await websocket.send_text(json.dumps({'type': 'calibration_updated', 'gauge_id': gauge_id}))
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
@app.get("/api/pressure")
async def get_pressure():
    return latest_state
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
