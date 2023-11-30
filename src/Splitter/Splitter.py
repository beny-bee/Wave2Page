import demucs.api
import torch
from denoiser import pretrained
from denoiser.dsp import convert_audio
import os

class AudioSplitter:

    def __init__(self, SEPARATOR_BAR):
        self.karaoke_separator = demucs.api.Separator(model="htdemucs", progress=True)
        self.separator = demucs.api.Separator(model="htdemucs_6s", progress=True)
        self.denoiser = pretrained.dns64()
        self.SEPARATOR_BAR = SEPARATOR_BAR

    def separate(self, input_audio_path, output_audio_path):
        print('Separating audio sources...')
        origin, separated = self.karaoke_separator.separate_audio_file(input_audio_path)
        
        # Define the output directory for the separated audio files
        os.makedirs(output_audio_path, exist_ok=True)
        
        for stem, source in separated.items():
            output_path = os.path.join(output_audio_path, f'{stem}.wav')
            if stem == 'vocals':
                print('Improving vocals...')
                improved = convert_audio(source, self.karaoke_separator.samplerate, self.denoiser.sample_rate, self.denoiser.chin)
                with torch.no_grad():
                    improved = self.denoiser(improved[None])[0]
                demucs.api.save_audio(improved, output_path, samplerate=self.denoiser.sample_rate)
            else:
                demucs.api.save_audio(source, output_path, samplerate=self.separator.samplerate)
            if stem == "other":
                output_path_others = output_path
            
        origin, separated = self.separator.separate_audio_file(output_path_others)
        for stem, source in separated.items():
            if stem in ['piano', 'guitar', 'other']:
                output_path = os.path.join(output_audio_path, f'{stem}.wav')
                demucs.api.save_audio(source, output_path, samplerate=self.separator.samplerate)
        
        print(f"Succesfully separated audio. Results in {output_audio_path}")
        