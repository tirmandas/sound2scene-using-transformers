import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model

class AudioProcessor:
    def __init__(self):
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        self.model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
        self.model.eval()

    def extract_embedding(self, wav_path):
        waveform, sample_rate = torchaudio.load(wav_path)

        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)

        input_values = self.processor(
            waveform.squeeze().numpy(),
            sampling_rate=16000,
            return_tensors="pt"
        ).input_values

        with torch.no_grad():
            outputs = self.model(input_values)

        embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding