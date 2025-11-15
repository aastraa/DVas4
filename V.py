import open3d as o3d
import numpy as np

# =========================================================
#  Путь к 3D модели
# =========================================================
MODEL_PATH = "/Users/adilkhanmaratov/Downloads/Study/Data Visualization/wolf.ply"

# =========================================================
#  Универсальная функция визуализации (крутить можно мышкой)
# =========================================================
def show(title, objects):
    o3d.visualization.draw_geometries(
        objects,
        window_name=title,
        width=900,
        height=700,
        point_show_normal=False
    )

# =========================================================
# 1. Загрузка и отображение модели
# =========================================================
mesh = o3d.io.read_triangle_mesh(MODEL_PATH)

if not mesh.has_vertex_normals():
    mesh.compute_vertex_normals()

print("\n=== Шаг 1: Исходная модель ===")
print("Количество вершин:", len(mesh.vertices))
print("Количество треугольников:", len(mesh.triangles))
print("Есть цвета:", mesh.has_vertex_colors())
print("Есть нормали:", mesh.has_vertex_normals())

show("Step 1: Original Mesh", [mesh])

# =========================================================
# 2. Преобразование в облако точек
# =========================================================
pcd = mesh.sample_points_poisson_disk(number_of_points=3000)

print("\n=== Шаг 2: Point Cloud ===")
print("Количество точек:", len(pcd.points))
print("Есть цвета:", pcd.has_colors())

show("Step 2: Point Cloud", [pcd])

# =========================================================
# 3. Реконструкция поверхности Poisson
# =========================================================
mesh_poisson, dens = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd, depth=8
)
bbox = mesh.get_axis_aligned_bounding_box()
mesh_poisson = mesh_poisson.crop(bbox)

print("\n=== Шаг 3: Poisson Mesh ===")
print("Количество вершин:", len(mesh_poisson.vertices))
print("Количество треугольников:", len(mesh_poisson.triangles))
print("Есть цвета:", mesh_poisson.has_vertex_colors())

show("Step 3: Poisson Mesh", [mesh_poisson])

# =========================================================
# 4. Вокселизация
# =========================================================
voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=0.05)

print("\n=== Шаг 4: Voxel Grid ===")
print("Количество вокселей:", len(voxel_grid.get_voxels()))

show("Step 4: Voxel Grid", [voxel_grid])

# =========================================================
# 5. Плоскость для клиппинга
# =========================================================
points = np.asarray(pcd.points)

x_min, x_max = points[:, 0].min(), points[:, 0].max()
y_min, y_max = points[:, 1].min(), points[:, 1].max()
z_min, z_max = points[:, 2].min(), points[:, 2].max()

plane_x = (x_min + x_max) / 2  # режем модель пополам по X

plane = o3d.geometry.TriangleMesh.create_box(
    width=0.01,
    height=(y_max - y_min) + 0.2,
    depth=(z_max - z_min) + 0.2
)
plane.translate([plane_x, y_min - 0.1, z_min - 0.1])
plane.paint_uniform_color([1.0, 0.2, 0.2])  # красная плоскость

print("\n=== Шаг 5: Mesh + Plane ===")
show("Step 5: Mesh + Plane", [mesh, plane])

# =========================================================
# 6. Клиппинг — удаляем правую часть
# =========================================================
mask = points[:, 0] < plane_x  # оставляем левую часть

pcd_clipped = o3d.geometry.PointCloud()
pcd_clipped.points = o3d.utility.Vector3dVector(points[mask])

print("\n=== Шаг 6: Clipped Model ===")
print("Количество точек:", len(pcd_clipped.points))

show("Step 6: Clipped Point Cloud", [pcd_clipped])

# =========================================================
# 7. Цвет + экстремальные точки (НА ПОЛНОЙ МОДЕЛИ)
# =========================================================
points_full = np.asarray(pcd.points)

# Градиент по оси Z
colors = (points_full - points_full.min(axis=0)) / \
         (points_full.max(axis=0) - points_full.min(axis=0))

pcd.colors = o3d.utility.Vector3dVector(colors)

# Экстремумы
min_z_idx = points_full[:, 2].argmin()
max_z_idx = points_full[:, 2].argmax()

min_point = points_full[min_z_idx]
max_point = points_full[max_z_idx]

print("\n=== Шаг 7: Extremes on FULL Model ===")
print("Минимум по Z:", min_point)
print("Максимум по Z:", max_point)

sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=0.02)
sphere_min.paint_uniform_color([1, 0, 0])
sphere_min.translate(min_point)

sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=0.02)
sphere_max.paint_uniform_color([0, 1, 0])
sphere_max.translate(max_point)

show("Step 7: Full Model with Extremes", [pcd, sphere_min, sphere_max])
