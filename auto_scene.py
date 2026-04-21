
import bpy
import math
import os
import random

objects = ['tsunami', 'water', 'wave', 'building']
# -----------------------
# CAPTION + OBJECT DISPLAY (SAFE ADDITION)
# -----------------------

def generate_caption(objects):
    if "earthquake" in objects:
        return "Earthquake destroying buildings with debris and cracks"
    elif "tsunami" in objects:
        return "Tsunami wave flooding buildings and urban area"
    elif "fire" in objects:
        return "Volcanic fire eruption burning trees with smoke"
    else:
        return "Unknown disaster scene"

caption = generate_caption(objects)

# Print in console (SAFE)
print("🎯 Caption:", caption)
print("📦 Scene Objects:", objects)

# -----------------------
# OPTIONAL: SHOW TEXT IN SCENE (NON-INTRUSIVE)
# -----------------------

bpy.ops.object.text_add(location=(0, -12, 10))
text_obj = bpy.context.view_layer.objects.active

text_obj.data.body = caption
text_obj.data.size = 1
text_obj.rotation_euler[0] = math.radians(90)

# Optional: simple material
text_mat = bpy.data.materials.new("TextMat")
text_mat.use_nodes = True
bsdf = text_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1,1,1,1)

text_obj.data.materials.append(text_mat)

# Reset Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 150
scene.render.engine = 'CYCLES'

# -----------------------
# MATERIAL FUNCTION
# -----------------------
def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    return mat

ground_mat = create_material("Ground", (0.4,0.4,0.4,1))
building_mat = create_material("Building", (0.6,0.6,0.6,1))

# -----------------------
# GROUND
# -----------------------
mesh = bpy.data.meshes.new("GroundMesh")
ground = bpy.data.objects.new("Ground", mesh)
scene.collection.objects.link(ground)

verts = [(-15,-15,0),(15,-15,0),(15,15,0),(-15,15,0)]
faces = [(0,1,2,3)]
mesh.from_pydata(verts, [], faces)
mesh.update()
ground.data.materials.append(ground_mat)

# -----------------------
# BUILDINGS
# -----------------------
buildings = []
positions = [(0,0), (6,2), (-5,-3)]

for i,pos in enumerate(positions):

    mesh = bpy.data.meshes.new(f"BuildingMesh{i}")
    obj = bpy.data.objects.new(f"Building{i}", mesh)
    scene.collection.objects.link(obj)

    height = random.uniform(6,10)

    verts = [
        (-2,-2,0),(2,-2,0),(2,2,0),(-2,2,0),
        (-2,-2,height),(2,-2,height),(2,2,height),(-2,2,height)
    ]

    faces = [(0,1,2,3),(4,5,6,7),
             (0,1,5,4),(1,2,6,5),
             (2,3,7,6),(3,0,4,7)]

    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj.location = (pos[0], pos[1], 0)
    obj.data.materials.append(building_mat)

    buildings.append(obj)

# -----------------------
# EARTHQUAKE (IMPROVED)
# -----------------------
if "earthquake" in objects:

    # Shake buildings
    for b in buildings:
        for frame in range(1,150,5):
            b.location.x += random.uniform(-0.15,0.15)
            b.location.y += random.uniform(-0.15,0.15)
            b.rotation_euler[0] += random.uniform(-0.08,0.08)
            b.rotation_euler[1] += random.uniform(-0.08,0.08)

            b.keyframe_insert(data_path="location", frame=frame)
            b.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Debris (ON GROUND ONLY)
    for i in range(15):
        bpy.ops.mesh.primitive_cube_add(
            size=0.4,
            location=(random.uniform(-6,6), random.uniform(-6,6), 0.2)
        )
        debris = bpy.context.view_layer.objects.active

        # small bounce instead of floating
        for frame in range(1,80,10):
            debris.location.z = random.uniform(0.1, 0.6)
            debris.keyframe_insert(data_path="location", frame=frame)

        debris.location.z = 0.2

    # REAL CRACKS (geometry)
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0,0,0.01))
    crack = bpy.context.view_layer.objects.active

    crack_mat = bpy.data.materials.new("CrackMat")
    crack_mat.use_nodes = True

    nodes = crack_mat.node_tree.nodes
    links = crack_mat.node_tree.links

    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 15

    ramp = nodes.new(type="ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0,0,0,1)
    ramp.color_ramp.elements[1].color = (0.1,0.1,0.1,1)

    bsdf = nodes["Principled BSDF"]

    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    crack.data.materials.append(crack_mat)
# -----------------------
# TSUNAMI (FINAL STABLE + REAL FLOW)
# -----------------------
if "tsunami" in objects:

    # -----------------------
    # DOMAIN (simulation box)
    # -----------------------
    bpy.ops.mesh.primitive_cube_add(location=(0,0,6))
    domain = bpy.context.view_layer.objects.active
    domain.scale = (20, 10, 8)

    fluid_mod = domain.modifiers.new(name="Fluid", type='FLUID')
    fluid_mod.fluid_type = 'DOMAIN'

    d = fluid_mod.domain_settings
    d.domain_type = 'LIQUID'
    d.resolution_max = 64
    d.use_mesh = True
    d.cache_frame_end = 250

    # -----------------------
    # FLOW (SEA WATER SOURCE)
    # -----------------------
    bpy.ops.mesh.primitive_cube_add(location=(-18,0,3))
    flow = bpy.context.view_layer.objects.active
    flow.scale = (6, 10, 3)

    flow_mod = flow.modifiers.new(name="Fluid", type='FLUID')
    flow_mod.fluid_type = 'FLOW'

    f = flow_mod.flow_settings
    f.flow_type = 'LIQUID'
    f.flow_behavior = 'INFLOW'

    # 👉 THIS controls tsunami strength
    f.use_initial_velocity = True
    f.velocity_normal = 4

    # -----------------------
    # GROUND (collision)
    # -----------------------
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0,0,0))
    ground = bpy.context.view_layer.objects.active

    ground_mod = ground.modifiers.new(name="Fluid", type='FLUID')
    ground_mod.fluid_type = 'EFFECTOR'

    # -----------------------
    # BUILDINGS (collision)
    # -----------------------
    for b in buildings:
        mod = b.modifiers.new(name="Fluid", type='FLUID')
        mod.fluid_type = 'EFFECTOR'

    # -----------------------
    # WATER MATERIAL (REALISTIC)
    # -----------------------
    water_mat = bpy.data.materials.new("Water")
    water_mat.use_nodes = True

    nodes = water_mat.node_tree.nodes
    bsdf = nodes["Principled BSDF"]

    bsdf.inputs["Base Color"].default_value = (0.0,0.25,0.7,1)
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.05

   
    

    print("🌊 TSUNAMI Disaster stimulation")

# -----------------------
# FIRE SCENE (VOLCANO + TREES - FINAL STABLE)
# -----------------------
if "fire" in objects:

    import random

    # -----------------------
    # GROUND
    # -----------------------
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0,0,0))
    ground = bpy.context.view_layer.objects.active

    # -----------------------
    # VOLCANO (CRATER - NO ERRORS)
    # -----------------------
    bpy.ops.mesh.primitive_cone_add(radius1=4, depth=8, location=(-8,0,4))
    volcano = bpy.context.view_layer.objects.active

    # cutter for crater
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=3, location=(-8,0,8))
    cutter = bpy.context.view_layer.objects.active

    # boolean modifier (NO APPLY → no crash)
    bool_mod = volcano.modifiers.new(name="Crater", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter

    # hide cutter instead of deleting
    cutter.hide_viewport = True
    cutter.hide_render = True

    # -----------------------
    # TREES
    # -----------------------
    trees = []

    for i in range(6):
        x = random.uniform(2,10)
        y = random.uniform(-6,6)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=2, location=(x,y,1))
        trunk = bpy.context.view_layer.objects.active

        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x,y,2.5))
        leaves = bpy.context.view_layer.objects.active

        trees.append((trunk, leaves))

    # -----------------------
    # LAVA MATERIAL
    # -----------------------
    mat = bpy.data.materials.new("LavaMat")
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    emission = nodes.new(type="ShaderNodeEmission")
    emission.inputs["Color"].default_value = (1,0.2,0,1)
    emission.inputs["Strength"].default_value = 120

    output = nodes["Material Output"]
    links.new(emission.outputs["Emission"], output.inputs["Surface"])

    # -----------------------
    # LAVA (CRATER)
    # -----------------------
    bpy.ops.mesh.primitive_uv_sphere_add(location=(-8,0,7))
    lava = bpy.context.view_layer.objects.active
    lava.scale = (1.2,1.2,1.2)
    lava.data.materials.append(mat)

    lava.keyframe_insert("location", frame=1)
    lava.location = (-8,0,12)
    lava.keyframe_insert("location", frame=40)
    lava.location = (-8,0,7)
    lava.keyframe_insert("location", frame=80)

    # -----------------------
    # LAVA FLOW DOWN
    # -----------------------
    for i in range(6):
        bpy.ops.mesh.primitive_uv_sphere_add(
            location=(-8 + i*1.2, 0, 6 - i*0.8)
        )
        flow = bpy.context.view_layer.objects.active
        flow.scale = (0.8,0.8,0.5)
        flow.data.materials.append(mat)

    # -----------------------
    # FIRE + BURN TREES
    # -----------------------
    for (trunk, leaves) in trees:

        burn_mat = bpy.data.materials.new("Burnt")
        burn_mat.use_nodes = True
        bsdf = burn_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.1,0.05,0.02,1)

        leaves.data.materials.append(burn_mat)

        bpy.ops.mesh.primitive_cone_add(
            radius1=0.5,
            depth=2,
            location=(trunk.location.x, trunk.location.y, 2)
        )
        fire = bpy.context.view_layer.objects.active
        fire.data.materials.append(mat)

        for f in range(1,120,10):
            fire.scale = (
                random.uniform(0.5,1),
                random.uniform(0.5,1),
                random.uniform(1,2)
            )
            fire.keyframe_insert("scale", frame=f)

    # -----------------------
    # SMOKE
    # -----------------------
    bpy.ops.mesh.primitive_cube_add(location=(-8,0,9))
    smoke = bpy.context.view_layer.objects.active
    smoke.scale = (2,2,4)

    smoke_mat = bpy.data.materials.new("Smoke")
    smoke_mat.use_nodes = True

    nodes = smoke_mat.node_tree.nodes
    links = smoke_mat.node_tree.links

    volume = nodes.new(type="ShaderNodeVolumePrincipled")
    volume.inputs["Density"].default_value = 6
    volume.inputs["Color"].default_value = (0.05,0.05,0.05,1)

    output = nodes["Material Output"]
    links.new(volume.outputs["Volume"], output.inputs["Volume"])

    smoke.data.materials.append(smoke_mat)

    smoke.keyframe_insert("location", frame=1)
    smoke.location = (-8,0,18)
    smoke.keyframe_insert("location", frame=120)

    print("🔥 FINAL VOLCANO FIRE WORKING")

# -----------------------
# CINEMATIC CAMERA
# -----------------------
cam_data = bpy.data.cameras.new("Camera")
camera = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(camera)

# Start position
camera.location = (25,-25,18)
camera.rotation_euler = (math.radians(65),0,math.radians(45))
camera.keyframe_insert("location", frame=1)

# Move closer to wave
camera.location = (10,-15,12)
camera.keyframe_insert("location", frame=140)

scene.camera = camera





# -----------------------
# LIGHT
# -----------------------
light_data = bpy.data.lights.new(name="Sun", type='SUN')
light = bpy.data.objects.new(name="Sun", object_data=light_data)
scene.collection.objects.link(light)
light.location = (10,-10,15)

# -----------------------
# SOUND (FINAL FIX)
# -----------------------
sound_path = r"C:\Users\tirmandas\Desktop\sound2scene\sounds\tsunami.wav"

if os.path.exists(sound_path):

    if not scene.sequence_editor:
        scene.sequence_editor_create()

    scene.sequence_editor.strips.new_sound(
        name="Sound",
        filepath=sound_path,
        channel=1,
        frame_start=1
    )

print("FINAL MULTI-DISASTER SYSTEM READY")
