import open3d as o3d
import numpy as np
import random


class SceneComposer:

    def compose_scene(self, objects):
        geometries = []

        for obj in objects:

            if obj == "ground":
                mesh = o3d.geometry.TriangleMesh.create_box(10, 0.1, 10)
                mesh.paint_uniform_color([0.4, 0.4, 0.4])

            elif obj == "building":
                mesh = o3d.geometry.TriangleMesh.create_box(1.5, 4, 1.5)
                mesh.translate([0, 0.1, 0])
                mesh.paint_uniform_color([0.7, 0.7, 0.7])

                # Add second building
                mesh2 = o3d.geometry.TriangleMesh.create_box(1.5, 3, 1.5)
                mesh2.translate([3, 0.1, 2])
                mesh2.paint_uniform_color([0.6, 0.6, 0.6])
                geometries.append(mesh2)

            elif obj == "explosion":
                mesh = o3d.geometry.TriangleMesh.create_sphere(radius=1)
                mesh.translate([0, 2, 0])
                mesh.paint_uniform_color([1, 0.3, 0])

                # Add debris pieces
                for _ in range(8):
                    debris = o3d.geometry.TriangleMesh.create_sphere(radius=0.3)
                    debris.translate([
                        random.uniform(-2, 2),
                        random.uniform(0.2, 1),
                        random.uniform(-2, 2)
                    ])
                    debris.paint_uniform_color([0.4, 0.2, 0.1])
                    geometries.append(debris)

            elif obj == "smoke":
                for i in range(4):
                    smoke = o3d.geometry.TriangleMesh.create_sphere(radius=1 + i*0.3)
                    smoke.translate([0, 3 + i*0.5, 0])
                    smoke.paint_uniform_color([0.3, 0.3, 0.3])
                    geometries.append(smoke)
                continue

            elif obj == "water":
                mesh = o3d.geometry.TriangleMesh.create_box(8, 0.3, 8)
                mesh.paint_uniform_color([0, 0.4, 1])

            else:
                continue

            geometries.append(mesh)

        return geometries