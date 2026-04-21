import torch
import laion_clap

class DisasterCaptionGenerator:
    def __init__(self):
        self.model = laion_clap.CLAP_Module(enable_fusion=False)
        self.model.load_ckpt()

        self.disaster_prompts = [
            "A building on fire with heavy smoke",
            "Severe flooding tsunami in an urban area",
            "An explosion damaging infrastructure",
            "Earthquake destroying buildings",
            "Crowd panic during emergency evacuation"
        ]

    def generate_caption(self, wav_path):
        audio_embed = self.model.get_audio_embedding_from_filelist([wav_path])
        text_embed = self.model.get_text_embedding(self.disaster_prompts)

        audio_embed = torch.tensor(audio_embed)
        text_embed = torch.tensor(text_embed)

        similarity = torch.matmul(audio_embed, text_embed.T)
        best_match = torch.argmax(similarity).item()

        return self.disaster_prompts[best_match]