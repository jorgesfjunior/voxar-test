# 1. Importing Libraries
import os
import time
import tracemalloc
from memory_profiler import memory_usage
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from PIL import Image
import torch
from transformers import GLPNImageProcessor, GLPNForDepthEstimation
import numpy as np
import open3d as o3d

# Benchmark file setup
output_dir = './results/'  # Directory to save outputs
os.makedirs(output_dir, exist_ok=True)
benchmark_file = os.path.join(output_dir, 'benchmarks.txt')

with open(benchmark_file, 'w') as f:
    f.write("Benchmark Results\n")
    f.write("=================\n\n")

# 2. Getting Model
feature_extractor = GLPNImageProcessor.from_pretrained("vinvino02/glpn-nyu")
model = GLPNForDepthEstimation.from_pretrained("vinvino02/glpn-nyu")

# 3. Directory with images
input_dir = './data/'  # Directory with input images

# 4. Processing multiple images
for filename in os.listdir(input_dir):
    if not filename.endswith(('.png', '.jpg', '.jpeg')):
        continue

    # Start benchmarks
    start_time = time.time()
    tracemalloc.start()
    initial_memory = memory_usage()[0]

    # Loading and resizing the image
    image_path = os.path.join(input_dir, filename)
    image = Image.open(image_path)
    image = image.convert("RGB")
    new_height = 480 if image.height > 480 else image.height
    new_height -= (new_height % 32)
    new_width = int(new_height * image.width / image.height)
    diff = new_width % 32
    new_width = new_width - diff if diff < 16 else new_width + 32 - diff
    new_size = (new_width, new_height)
    image = image.resize(new_size)

    # Preparing the image for the model
    inputs = feature_extractor(images=image, return_tensors='pt')

    # Getting the prediction from the model
    with torch.no_grad():
        outputs = model(**inputs)
        predicted_depth = outputs.predicted_depth

    # Post-processing
    pad = 16
    output = predicted_depth.squeeze().cpu().numpy() * 1000.0
    output = output[pad:-pad, pad:-pad]
    image = image.crop((pad, pad, image.width - pad, image.height - pad))

    # Preparing the depth image for Open3D
    width, height = image.size
    depth_image = (output * 255 / np.max(output)).astype('uint8')
    image = np.array(image)

    depth_o3d = o3d.geometry.Image(depth_image)
    image_o3d = o3d.geometry.Image(image)
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        image_o3d, depth_o3d, depth_scale=1000.0, depth_trunc=3.0, convert_rgb_to_intensity=False)

    # Creating a camera
    camera_intrinsic = o3d.camera.PinholeCameraIntrinsic()
    camera_intrinsic.set_intrinsics(width, height, 500, 500, width / 2, height / 2)

    # Creating a 3D point cloud
    pcd_raw = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, camera_intrinsic)

    # Post-processing the 3D point cloud
    cl, ind = pcd_raw.remove_statistical_outlier(nb_neighbors=20, std_ratio=6.0)
    pcd = pcd_raw.select_by_index(ind)
    pcd.estimate_normals()
    pcd.orient_normals_to_align_with_direction()

    # Surface reconstruction
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=10, n_threads=1)[0]

    # Rotate the mesh
    rotation = mesh.get_rotation_matrix_from_xyz((np.pi, 0, 0))
    mesh.rotate(rotation, center=(0, 0, 0))

    # Save the mesh
    output_mesh_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.obj")
    o3d.io.write_triangle_mesh(output_mesh_path, mesh)

    # End benchmarks
    end_time = time.time()
    peak_memory = memory_usage()[0] - initial_memory
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Log results
    with open(benchmark_file, 'a') as f:
        f.write(f"Image: {filename}\n")
        f.write(f"Execution Time: {end_time - start_time:.2f} seconds\n")
        f.write(f"Peak Memory Usage: {peak_memory:.2f} MB\n")
        f.write(f"Peak VRAM Usage: {peak / 1e6:.2f} MB\n")
        f.write("\n")

    print(f"Processed {filename} and saved to {output_mesh_path}")

print("Processing completed.")
