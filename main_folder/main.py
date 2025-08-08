from ophyd import EpicsMotor, EpicsSignal
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector import AreaDetector, ADComponent, ImagePlugin, JPEGPlugin, TIFFPlugin
from ophyd.areadetector.cam import AreaDetectorCam
from ophyd.areadetector.cam import CamBase
from bluesky import RunEngine
from databroker import Broker, temp
from bluesky.plans import scan, count
import bluesky.plan_stubs as bps
import numpy as np
from datetime import datetime
from pathlib import Path
from PIL import Image
import time
import os
from collections import defaultdict
class PvaPlugin(PluginBase):
    _suffix = 'Pva1:'
    _plugin_type = 'NDPluginPva'
    _default_read_attrs = ['enable']
    _default_configuration_attrs = ['enable']

    array_callbacks = ADComponent(EpicsSignal, 'ArrayCallbacks')

# Create RunEngine
RE = RunEngine({})

# Define the motor
motor = EpicsMotor('DMC01:A', name='motor')

# Define the camera deviceca
class MyCamera(AreaDetector):
    cam = ADComponent(AreaDetectorCam, 'cam1:') #Fixed the single camera issue?
    image = ADComponent(ImagePlugin, 'image1:')
    tiff = ADComponent(TIFFPlugin, 'TIFF1:')
    pva = ADComponent(PvaPlugin, 'Pva1:')

# Instantiate the camera
camera = MyCamera('13ARV1:', name='camera')
camera.wait_for_connection()

#CAM OPTIONS
camera.stage_sigs[camera.cam.acquire] = 0 
camera.stage_sigs[camera.cam.image_mode] = 0 # single multiple continuous
camera.stage_sigs[camera.cam.trigger_mode] = 0 # internal external

#IMAGE OPTIONS
camera.stage_sigs[camera.image.enable] = 1 # pva plugin
camera.stage_sigs[camera.image.queue_size] = 2000

#JPEG OPTIONS
camera.stage_sigs[camera.tiff.enable] = 1
camera.stage_sigs[camera.tiff.auto_save] = 1
camera.stage_sigs[camera.tiff.file_write_mode] = 0  # Or 'Single' works too
camera.stage_sigs[camera.tiff.nd_array_port] = 'SP1'  
camera.stage_sigs[camera.tiff.auto_increment] = 1       #Doesn't work, must be ignored

#PVA OPTIONS
camera.stage_sigs[camera.pva.enable] = 1
camera.stage_sigs[camera.pva.blocking_callbacks] = 'No'
camera.stage_sigs[camera.pva.queue_size] = 2000  # or higher
camera.stage_sigs[camera.pva.nd_array_port] = 'SP1' 
camera.stage_sigs[camera.pva.array_callbacks] = 0  # disable during scan


def wait_for_file(filepath, timeout=5.0, poll_interval=0.1):
    """Wait until a file appears on disk, or timeout."""
    start = time.time()
    while not os.path.exists(filepath):
        if time.time() - start > timeout:
            raise TimeoutError(f"Timed out waiting for file: {filepath}")
        time.sleep(poll_interval)

def scan_with_saves(start_pos, end_pos, num_points):
    yield from bps.mv(callbacks_signal, 0)
    max_retries = 50
    positions = np.linspace(start_pos, end_pos, num_points)
    yield from bps.open_run()
    camera.cam.array_callbacks.put(0, wait=True)

    print("\n--- Staging camera ---")
    yield from bps.stage(camera)

    current_number = camera.tiff.file_number.get()

    NUM_IMAGES_PER_POS = 20

    for i, pos in enumerate(positions):
        print(f"\nMoving to pos={pos}")
        yield from bps.mv(motor, pos)
        yield from bps.sleep(2.0) 
        yield from bps.mv(acquire_signal, 0)  # Triggers a single image

        #for img_idx in range(NUM_IMAGES_PER_POS):
        filename = f'scan_{timestamp}_pos_{i}_shot'           
        current_number += 1
        filepath = os.path.join(save_dir, f"{filename}_{current_number}.tiff")

        yield from bps.mv(camera.tiff.file_name, filename)
        yield from bps.mv(camera.tiff.file_number, current_number)

        for attempt in range(1, max_retries + 1):

            try:
                print(f"[Attempt {attempt}] Capturing → {filepath}")
                yield from bps.mv(acquire_signal, 1)  # Triggers a single image
                yield from bps.sleep(1)

                # Wait for file to appear
                wait_for_file(filepath, timeout=5.0)

                print(f"✓ Image saved at {filepath}")
                break  # Exit retry loop if successful

            except TimeoutError:
                print(f"--Timeout waiting for image at {filepath}")
                if attempt == max_retries:
                    print(f"--Failed after {max_retries} attempts, skipping position {pos}")
                else:
                    print("↻ Retrying acquisition...")
                    yield from bps.mv(acquire_signal, 0)  # Triggers a single image
                    yield from bps.sleep(0.5)
    
    print("\n--- Unstaging camera ---")
    yield from bps.unstage(camera)

    yield from bps.mv(motor, 0.0)
    yield from bps.close_run()

def cropImages(inputDir):
    crop_box = (800, 800, 1600, 1500)
    output_dir = inputDir.replace('raw_images/', 'images/')

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(inputDir):
        if filename.endswith('.tiff'):
            image_path = os.path.join(inputDir, filename)
            img = Image.open(image_path)
            cropped = img.crop(crop_box)
            cropped.save(os.path.join(output_dir, filename))

def average_images_per_position(image_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    grouped = defaultdict(list)

    for fname in os.listdir(image_dir):
        if fname.endswith('.tiff') and 'pos_' in fname:
            pos_id = fname.split('pos_')[1].split('_')[0]
            grouped[pos_id].append(fname)

    for pos, files in grouped.items():
        print(f"Averaging {len(files)} images for position {pos}")
        avg_array = None
        for fname in files:
            img = Image.open(os.path.join(image_dir, fname)).convert('RGB')
            arr = np.array(img).astype(np.float32)
            if avg_array is None:
                avg_array = arr
            else:
                avg_array += arr
        avg_array /= len(files)
        avg_img = Image.fromarray(np.clip(avg_array, 0, 255).astype(np.uint8))
        avg_img.save(os.path.join(output_dir, f"average_pos_{pos}.jpg"))

# Run scan
try:
    #Requirements for image capturing
    acquire_signal = EpicsSignal('13ARV1:cam1:Acquire', name='acquire_signal')
    callbacks_signal = EpicsSignal('13ARV1:image1:EnableCallbacks', name='callbacks_signal')

    # File configuration
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_dir = '/home/user/tmpData/scan/bolt_scan_15/raw_images/'

    # Ensure the directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Then set the path in EPICS
    camera.tiff.file_path.put(save_dir)             #what sets file path in saves
    camera.tiff.file_template.put('%s%s_%d.tiff')

    #Let's try above 95.5 to connect teh full circle
    RE(scan_with_saves(start_pos=0, end_pos=95.5, num_points=36))

    cropImages(save_dir)
    #cropped_dir = save_dir.replace('imagess/', 'images/')
    #average_output_dir = os.path.join(cropped_dir, 'averaged')
    #average_images_per_position(cropped_dir, average_output_dir)

except KeyboardInterrupt:
    print("\nScan interrupted by user")
    RE.stop()
except Exception as e:
    print(f"\nError during scan: {e}")
    #RE.stop()