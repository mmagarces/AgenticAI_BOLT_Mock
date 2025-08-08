"""
BOLT Agentic AI Controller - Device Connections
This module contains classes for connecting to BOLT devices using ophyd-websocket.
"""

import json
import time
import threading
import numpy as np
import websocket

class OphydWebsocketDevice:
    """Class to connect to EPICS devices via ophyd-websocket."""
    
    def __init__(self, pv_name, ws_url="ws://localhost:8000/ophydSocket"):
        self.pv_name = pv_name
        self.ws_url = ws_url
        self.value = None
        self.connected = False
        self.ws = None
        self.lock = threading.Lock()
        
        # Connect to the websocket
        self._connect()
    
    def _connect(self):
        """Connect to the ophyd websocket."""
        try:
            self.ws = websocket.create_connection(self.ws_url)
            
            # Subscribe to the PV
            subscribe_message = {
                "action": "subscribe",
                "pv": self.pv_name
            }
            self.ws.send(json.dumps(subscribe_message))
            
            # Start a thread to receive updates
            self.update_thread = threading.Thread(target=self._receive_updates)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            print(f"Connected to {self.pv_name}")
        except Exception as e:
            print(f"Error connecting to {self.pv_name}: {e}")
    
    def _receive_updates(self):
        """Thread to receive websocket updates."""
        try:
            while True:
                message = self.ws.recv()
                data = json.loads(message)
                
                # Check if this message is for our PV
                if "pv" in data and data["pv"] == self.pv_name:
                    with self.lock:
                        if "value" in data:
                            self.value = data["value"]
                        if "connected" in data:
                            self.connected = data["connected"]
                        
                        print(f"Updated {self.pv_name}: value={self.value}, connected={self.connected}")
        except Exception as e:
            print(f"Error in websocket update thread: {e}")
    
    def set(self, value):
        """Set the value of the PV."""
        if not self.connected:
            print(f"Error: {self.pv_name} is not connected")
            return None
        
        try:
            set_message = {
                "action": "set",
                "pv": self.pv_name,
                "value": value
            }
            self.ws.send(json.dumps(set_message))
            return value
        except Exception as e:
            print(f"Error setting value for {self.pv_name}: {e}")
            return None
    
    def read(self):
        """Read the current value of the PV."""
        with self.lock:
            return self.value
    
    def close(self):
        """Close the websocket connection."""
        if self.ws:
            try:
                unsubscribe_message = {
                    "action": "unsubscribe",
                    "pv": self.pv_name
                }
                self.ws.send(json.dumps(unsubscribe_message))
                self.ws.close()
            except:
                pass


class BoltSampleStage:
    """BOLT sample stage with rotation motor."""
    def __init__(self, ws_url="ws://localhost:8000/ophydSocket"):
        # Replace with the actual PV name for rotation motor in your BOLT setup
        self.rotation = OphydWebsocketDevice("BOLT:SampleStage:Rotation", ws_url)


class BoltDetector:
    """BOLT detector."""
    def __init__(self, ws_url="ws://localhost:8000/ophydSocket"):
        # Replace with the actual PV names for your detector
        self.acquire = OphydWebsocketDevice("BOLT:Detector:Acquire", ws_url)
        self.image = OphydWebsocketDevice("BOLT:Detector:Image", ws_url)
    
    def trigger(self):
        """Trigger the detector to take an image."""
        self.acquire.set(1)  # Usually 1 means start acquisition
        time.sleep(0.5)  # Give the detector time to acquire
        return True
    
    def read(self):
        """Read the image data from the detector."""
        # In a real system, you'd get the image data from the PV
        # For this example, we'll simulate data
        real_data = self.image.read()
        
        if real_data is not None and isinstance(real_data, (list, np.ndarray)):
            try:
                return np.array(real_data)
            except:
                pass
        
        # Generate simulated data if real data isn't available
        data = np.random.rand(512, 512)
        angle = self.acquire.read() or 0
        x, y = np.ogrid[-256:256, -256:256]
        center_x = 50 * np.cos(np.radians(angle))
        center_y = 50 * np.sin(np.radians(angle))
        mask = (x-center_x)**2 + (y-center_y)**2 <= 100**2
        data[mask] = 1.0
        return data


def connect_to_bolt(ws_url="ws://localhost:8000/ophydSocket"):
    """Connect to BOLT server via ophyd-websocket."""
    print(f"Connecting to BOLT server via {ws_url}")
    try:
        sample_stage = BoltSampleStage(ws_url)
        detector = BoltDetector(ws_url)
        return sample_stage, detector
    except Exception as e:
        print(f"Error connecting to BOLT: {e}")
        # Fall back to mock devices if connection fails
        print("Falling back to mock devices for testing")
        from mock_bolt import MockSampleStage, MockDetector
        return MockSampleStage(), MockDetector()
