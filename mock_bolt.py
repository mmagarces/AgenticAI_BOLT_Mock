"""
Fixed mock classes for BOLT devices when the real connection is unavailable.
Used as a fallback for testing when the ophyd-websocket connection fails.
"""

import numpy as np
import time

class MockBoltDevice:
    """Mock class for BOLT devices."""
    def __init__(self, name):
        self.name = name
        self.value = 0
        self.connected = True
        print(f"Initialized mock {name}")
        
    def set(self, value):
        self.value = value
        print(f"{self.name} moved to {value}")
        return self.value
    
    def read(self):
        return self.value
    
    def close(self):
        """Mock close method."""
        pass

class MockSampleStage:
    """Mock sample stage with rotation motor."""
    def __init__(self):
        self.rotation = MockBoltDevice("SampleStage.Rotation")

class MockDetector:
    """Mock detector that returns simulated data."""
    def __init__(self, name="Detector"):
        self.name = name
        self.acquire = MockBoltDevice(f"{name}.Acquire")
        self.image = MockBoltDevice(f"{name}.Image")
        
    def trigger(self):
        print(f"Triggered {self.name}")
        self.acquire.set(1)
        time.sleep(0.1)  # Simulate acquisition time
        return True
    
    def read(self):
        # Generate fake tomography projection
        angle = self.acquire.read()
        
        # Ensure we have a valid angle even if None
        if angle is None:
            angle = 0
            
        # Create simulation data
        data = np.random.rand(512, 512) * 0.1  # Low noise background
        
        # Add a simple circle pattern that changes with rotation angle
        x, y = np.ogrid[-256:256, -256:256]
        center_x = 50 * np.cos(np.radians(angle if angle is not None else 0))
        center_y = 50 * np.sin(np.radians(angle if angle is not None else 0))
        mask = (x-center_x)**2 + (y-center_y)**2 <= 100**2
        data[mask] = 1.0
        
        # Add some noise
        data += np.random.rand(512, 512) * 0.05
        
        return data

def connect_to_mock_bolt():
    """Create mock devices for testing."""
    print("Creating mock devices for testing")
    return MockSampleStage(), MockDetector()