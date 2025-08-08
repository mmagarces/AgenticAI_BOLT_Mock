
import os
import subprocess
import time

def run_openmvs_pipeline(base_path, image_dir, workspace_dir, colmap_path="colmap", image_file_name=None):
    database_path = os.path.join(workspace_dir, "database.db")
    sparse_dir = os.path.join(workspace_dir, "sparse")
    dense_dir = os.path.join(workspace_dir, "dense")

    dense_images = os.path.join(workspace_dir, "dense", "images")
    scene_mvs = os.path.join(dense_dir, "scene.mvs")
    dense_mvs = os.path.join(dense_dir, "scene_dense.mvs")

    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    # 1. Create scene.mvs
    subprocess.run([
        "/usr/local/bin/OpenMVS/InterfaceCOLMAP",
        #"-i", os.path.join(base_path, "workspace", "dense", "0"),   #Fix this from your colmap
        "-i", os.path.join(base_path, "workspace", "dense"),   #Fix this from your colmap
        "-o", scene_mvs,
        "--image-folder", image_dir
    ],cwd=dense_dir)
    
    # 2. Densify point cloud
    subprocess.run([
        "/usr/local/bin/OpenMVS/DensifyPointCloud",
        scene_mvs
    ], cwd=dense_dir)
    
    # 3. Densify point cloud
    subprocess.run([
        "/usr/local/bin/OpenMVS/ReconstructMesh",
        dense_mvs
    ], cwd=dense_dir)
    
    # 4. Texture the Mesh (adds color!)
    subprocess.run([
        "/usr/local/bin/OpenMVS/TextureMesh", scene_mvs,
        "-m", "scene_dense_mesh.ply"
    ],cwd=dense_dir)
    
    print("openMVS pipeline completed.")

# Example usage
image_file_name = "bolt_scan_15"

base_path = "/home/user/tmpData/scan/"

current_directory = os.path.join(base_path, image_file_name)
image_dir = os.path.join(base_path, image_file_name, "images_png")
workspace_dir = os.path.join(base_path, image_file_name, "workspace")

t2 = time.time()
run_openmvs_pipeline(current_directory, image_dir, workspace_dir, image_file_name=image_file_name)
t3= time.time()
print(f"OpenMVS time: {t3 - t2:.2f}s")
