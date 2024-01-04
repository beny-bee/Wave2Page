import demucs.api
import torch
from denoiser import pretrained
from denoiser.dsp import convert_audio
import os

class AudioSplitter:

    def __init__(self, SEPARATOR_BAR, instruments=None):
        self.karaoke_separator = demucs.api.Separator(model="htdemucs", progress=True)
        self.separator = demucs.api.Separator(model="htdemucs_6s", progress=True)
        self.denoiser = pretrained.dns64()
        self.SEPARATOR_BAR = SEPARATOR_BAR
        if isinstance(instruments, list):
            self.instruments = instruments
        else:
            self.instruments = ["bass", "drums", "guitar", "other", "piano", "vocals"]

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
                self.saveAudio(improved, output_path, self.denoiser.sample_rate, stem)
            else:
                self.saveAudio(source, output_path, self.separator.samplerate, stem)
            if stem == "other":
                output_path_others = output_path
            
        origin, separated = self.separator.separate_audio_file(output_path_others)
        for stem, source in separated.items():
            if stem in ['piano', 'guitar', 'other']:
                output_path = os.path.join(output_audio_path, f'{stem}.wav')
                self.saveAudio(source, output_path, self.separator.samplerate, stem)
        
        print(f"Succesfully separated audio. Results in {output_audio_path}")

    def saveAudio(self, source, output_path, samplerate, instrument):
        if (instrument == "other") or (instrument in self.instruments):
            demucs.api.save_audio(source, output_path, samplerate=samplerate)


class AudioReconstructor:
    def __init__(self):
        self.model = self.load_model()

    def load_model(self):
        # Load your specific model here
        # This could be a super-resolution model, a denoising model, etc.
        pass

    def enhance_audio(self, audio, samplerate):
        # This is a placeholder for the enhancement process
        # In reality, you would pass your audio through the deep learning model here
        enhanced_audio = audio  # This would be the output of your model
        return enhanced_audio