class SceneGraphBuilder:

    def build_scene(self, caption):

        caption = caption.lower()

        if "earthquake" in caption:
            return ["earthquake", "ground", "building", "cracks", "debris"]

        elif "tsunami" in caption or "wave" in caption:
            return ["tsunami", "water", "wave", "building", "debris"]

        elif "fire" in caption or "explosion" in caption:
            return ["fire", "explosion", "smoke", "building"]

        elif "flood" in caption:
            return ["flood", "water", "building"]

        else:
            return ["normal_scene"]