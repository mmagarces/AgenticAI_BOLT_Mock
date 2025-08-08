from fastapi import FastAPI
import os
import subprocess

app = FastAPI()

env = "python"

#Proper format

@app.get("/move_motor_by/{amount}")
def move_motor_by(amount: int):
    try:
        #First get the current angle
        cmd = ["/opt/epics/base-7.0.4/bin/linux-x86_64/caget", "DMC01:A"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            value_str = result.stdout.strip().split()[-1]
            angle = float(value_str)
        else:
            print("Failed to get motor value:", result.stderr)

        move_to_angle = amount + angle
        degree_angle = move_to_angle * 2.8125

        cmd1 = ["/opt/epics/base-7.0.4/bin/linux-x86_64/caput", "DMC01:A", str(move_to_angle)]
        result1 = subprocess.run(cmd1, capture_output=True, text=True)
        
        if result1.returncode == 0:
            return f"Moved motor succesfully. Current angle, with true motor angles, {degree_angle}"
        else:
            print("Failed to get motor value:", result.stderr)



    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"
    
@app.get("/move_motor/{amount}")
def move_motor(amount: int):
    cmd = ["/opt/epics/base-7.0.4/bin/linux-x86_64/caput", "DMC01:A", str(amount)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return f"Failed to move motor:\n{result.stderr}"

    return {"message": f"Moved motor to true amout of {amount}"}

@app.get("/take_measurement")
def acquire_image():
    try:
        #First get the current angle
        cmd = ["/opt/epics/base-7.0.4/bin/linux-x86_64/caget", "DMC01:A"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            value_str = result.stdout.strip().split()[-1]
            angle = float(value_str)
            angle = angle * 2.8125   #Ratio
        else:
            print("Failed to take measurement value:", result.stderr)

        #If no errors during acquisiton, pass in the current location of the cube in order to formulate the 
        #files name properly during acquisition (Can be replaced, but visually this is better to understand)
        cmd1 = [env, "take_measurement.py", str(float(angle))]
        result1 = subprocess.run(cmd1, capture_output=True, text=True)
        if result1.returncode == 0:
            return "Measurement succesfully taken"

    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"
    
@app.get("/get_angle")
def get_angle():
    try:
        #Get the current angle
        cmd = ["/opt/epics/base-7.0.4/bin/linux-x86_64/caget", "DMC01:A"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            value_str = result.stdout.strip().split()[-1]
            angle = float(value_str)
            angle = angle * 2.8125   #Ratio
        else:
            print("Failed to get angle value:", result.stderr)

        return f"Current angle is {angle}"

    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"

@app.get("/run_scan/{start_angle}/{end_angle}/{num_projections}/{save_dir}")
def run_scan_full(start_angle: int, end_angle: int, num_projections: int, save_dir: str):
    try:
        start_angle = float(start_angle) / 2.8125
        end_angle = float(end_angle) / 2.8125
        num_projections = int(num_projections)
        
        print(f"Running tomography scan from {start_angle * 2.8125} to {end_angle * 2.8125} degrees with {num_projections} projections, saving to {save_dir}")

        cmd = [env, 'run_tomography_scan.py', str(start_angle), str(end_angle), str(num_projections), str(save_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Scan failed:\n{result.stderr}"
        
        result_message = {
            f"Completed tomography scan with {num_projections} projections from {start_angle} to {end_angle} degrees"
            f"Original images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/uncropped_images/"
            f"Cropped images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/images/" }
        
        return result_message

    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"
    
@app.get("/run_scan/{start_angle}/{end_angle}/{num_projections}/") # Hard wired three entries will not include save_dir, but num_projections, start and end angles.
def run_scan_3(start_angle: int, end_angle: int, num_projections: int):
    try:
        start_angle = float(start_angle) / 2.8125
        end_angle = float(end_angle) / 2.8125
        num_projections = int(num_projections)
        save_dir = "default"
        
        print(f"Running tomography scan from {start_angle * 2.8125} to {end_angle * 2.8125} degrees with {num_projections} projections, saving to {save_dir}")

        cmd = [env, 'run_tomography_scan.py', str(start_angle), str(end_angle), str(num_projections), str(save_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Scan failed:\n{result.stderr}"
        
        result_message = {
            f"Completed tomography scan with {num_projections} projections from {start_angle} to {end_angle} degrees"
            f"Original images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/uncropped_images/"
            f"Cropped images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/images/" }
        
        return result_message

    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"

@app.get("/run_scan/{start_angle}/{end_angle}/") #Hard wired two entries will be angle  (Could be save dir, or num_projections)
def run_scan_2(start_angle: int, end_angle: int):
    try:
        start_angle = float(start_angle) / 2.8125
        end_angle = float(end_angle) / 2.8125
        num_projections = 10
        save_dir = "default"
        
        print(f"Running tomography scan from {start_angle * 2.8125} to {end_angle * 2.8125} degrees with {num_projections} projections, saving to {save_dir}")

        cmd = [env, 'run_tomography_scan.py', str(start_angle), str(end_angle), str(num_projections), str(save_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Scan failed:\n{result.stderr}"
        
        result_message = {
            f"Completed tomography scan with {num_projections} projections from {start_angle} to {end_angle} degrees"
            f"Original images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/uncropped_images/"
            f"Cropped images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/images/" }
        
        return result_message

    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"

@app.get("/run_scan/{num_projections}/") #Hard coded single entry will be num projections (Could be save dir but)
def run_scan_1(num_projections: int):
    try:
        start_angle = 0
        end_angle = 128
        num_projections = float(num_projections)
        save_dir = "default"
        
        print(f"Running tomography scan from {start_angle * 2.8125} to {end_angle * 2.8125} degrees with {num_projections} projections, saving to {save_dir}")

        cmd = [env, 'run_tomography_scan.py', str(start_angle), str(end_angle), str(num_projections), str(save_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Scan failed:\n{result.stderr}"
        
        result_message = {
            f"Completed tomography scan with {num_projections} projections from {start_angle} to {end_angle} degrees"
            f"Original images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/uncropped_images/"
            f"Cropped images saved to '/home/user/tmpData/AI_scan/" + save_dir + "/images/" }
        
        return result_message

    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"
    
@app.get("/reconstruction/{file_name}/")
def reconstruction(file_name: str):
    try:
        print(f"Running reconstruction on {file_name}")

        cmd = [env, 'reconstruction.py', file_name]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return f"Motor move failed:\n{result.stderr}"
        else:
             return f"Reconstruction succeeded"
    except Exception as e:
            print(f"Error getting current angle: {e}")
            return f"Error getting current angle: {str(e)}"


