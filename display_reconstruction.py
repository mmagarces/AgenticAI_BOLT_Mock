import open3d as o3d
import sys

def window(folder):
    mesh = o3d.io.read_triangle_mesh(folder)
    mesh.compute_vertex_normals()

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Custom Background", width=1280, height=720)
    vis.add_geometry(mesh)

    # Set background color (RGB range: 0–1)
    opt = vis.get_render_option()
    opt.background_color = [0.1, 0.1, 0.1]  # dark gray

    vis.run()
    vis.destroy_window()

if __name__ == "__main__":
    reconstruction_folder = sys.argv[1]

    window(reconstruction_folder)
