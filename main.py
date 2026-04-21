import subprocess
import sys
import os

from blender_script_generator import BlenderScriptGenerator

def run_pipeline(disaster_type):

    disaster_type = disaster_type.lower()

    print("Selected Disaster:", disaster_type)

    disaster_map = {
        "earthquake": ["earthquake", "ground", "building", "cracks"],
        "tsunami": ["tsunami", "water", "wave", "building"],
        "fire": ["fire", "trees", "smoke"]
    }

    sound_map = {
        "earthquake": "sounds/earthquake.wav",
        "tsunami": "sounds/tsunami.wav",
        "fire": "sounds/fire.wav"
    }

    if disaster_type not in disaster_map:
        print("❌ Invalid disaster. Use: earthquake | tsunami | fire")
        return

    objects = disaster_map[disaster_type]
    wav_path = sound_map[disaster_type]

    print("Scene Objects:", objects)
    print("Sound:", wav_path)

    generator = BlenderScriptGenerator()
    script_path = generator.generate_script(objects, wav_path)

    blender_path = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"

    subprocess.Popen([
        blender_path,
        "--python",
        os.path.abspath(script_path)
    ])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [earthquake|tsunami|fire]")
    else:
        run_pipeline(sys.argv[1])