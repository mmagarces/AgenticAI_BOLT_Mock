import os
import subprocess
import shutil
from PIL import Image
import time

def run_colmap_pipeline(image_dir, workspace_dir, colmap_path="colmap"):
    print("Running COLMAP pipeline with:")
    print(" - Image path:", image_dir)
    print(" - Workspace:", workspace_dir)

    database_path = os.path.join(workspace_dir, "database.db")
    dense_dir = os.path.join(workspace_dir, "dense")
    sparse_dir = os.path.join(workspace_dir, "sparse")
    undistorted_dir = os.path.join(dense_dir, "images")

    if os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir)
    os.makedirs(workspace_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)
    os.makedirs(sparse_dir, exist_ok=True)
    
    # 1. Feature extraction
    subprocess.run([
        colmap_path, "feature_extractor",
        "--database_path", database_path,
        "--image_path", image_dir,
        "--SiftExtraction.use_gpu", "0",
        "--SiftExtraction.num_threads", "6"  # or 1 to be safe
    ], check=True)
    
    # 2. Feature matching
    subprocess.run([
        colmap_path, "exhaustive_matcher",      #changed from exhaustive that does every image
        "--database_path", database_path,
        "--SiftMatching.use_gpu", "0",
    ], check=True)

    # 3. Sparse reconstruction
    '''
    subprocess.run([
        colmap_path, "mapper",
        "--database_path", database_path,
        "--image_path", image_dir,
        "--output_path", sparse_dir
    ],check=True)
    '''

    subprocess.run([
    colmap_path, "mapper",
        "--database_path", database_path,
        "--image_path", image_dir,
        "--output_path", sparse_dir,
    ], check=True)

    
    # 4. Image undistortion
    subprocess.run([
        colmap_path, "image_undistorter",
        "--image_path", image_dir,
        "--input_path", os.path.join(sparse_dir, "0"),
        "--output_path", dense_dir,           # must be just dense/
        "--output_type", "COLMAP"
    ],check=True)
    
    print("COLMAP pipeline completed.")

def convert_image_format(image_dir: str, output_image_dir: str):
    os.makedirs(output_image_dir, exist_ok=True)

    for filename in os.listdir(image_dir):
        if filename.lower().endswith(".tiff") or filename.lower().endswith(".tif"):
            tiff_path = os.path.join(image_dir, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(output_image_dir, png_filename)

            with Image.open(tiff_path) as im:
                im.save(png_path, format="PNG")


#Example usage #2
image_file_name = "bolt_scan_15"
base_path = "/home/user/tmpData/scan/"
image_directory_preprocess = os.path.join(base_path, image_file_name, "images")
image_dir = os.path.join(base_path, image_file_name, "images_png")

if ((os.path.exists(image_dir)) == 0):
    convert_image_format(image_directory_preprocess, image_dir)

workspace_directory = os.path.join(base_path, image_file_name, "workspace")

t0 = time.time()
run_colmap_pipeline(image_dir, workspace_directory)
#automatic_reconstruction(image_dir, workspace_dir)
t1 = time.time()
print(f"COLMAP time: {t1 - t0:.2f}s")
