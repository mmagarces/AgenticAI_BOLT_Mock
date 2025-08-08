from ophyd import EpicsMotor, EpicsSignal
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector import AreaDetector, ADComponent, ImagePlugin, JPEGPlugin, TIFFPlugin
from ophyd.areadetector.cam import AreaDetectorCam

class PvaPlugin(PluginBase):
    _suffix = 'Pva1:'
    _plugin_type = 'NDPluginPva'
    _default_read_attrs = ['enable']
    _default_configuration_attrs = ['enable']

    array_callbacks = ADComponent(EpicsSignal, 'ArrayCallbacks')

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

acquire_signal = EpicsSignal('13ARV1:cam1:Acquire', name='acquire_signal')
callbacks_signal = EpicsSignal('13ARV1:image1:EnableCallbacks', name='callbacks_signal')


