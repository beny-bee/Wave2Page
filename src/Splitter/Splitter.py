import demucs.api
import os

class AudioSplitter:

    def __init__(self, SEPARATOR_BAR):
        self.karaoke_separator = demucs.api.Separator(model="htdemucs", progress=True)
        self.separator = demucs.api.Separator(model="htdemucs_6s", progress=True)
        self.SEPARATOR_BAR = SEPARATOR_BAR

    def separate(self, input_audio_path, output_audio_path):
        print('Separating audio sources...')
        origin, separated = self.karaoke_separator.separate_audio_file(input_audio_path)
        
        # Define the output directory for the separated audio files
        os.makedirs(output_audio_path, exist_ok=True)
        
        output_path_others = ''
        for stem, source in separated.items():
            output_path = os.path.join(output_audio_path, f'{stem}.wav')
            if stem == 'other':
                output_path_others = output_path
            demucs.api.save_audio(source, output_path, samplerate=self.separator.samplerate)
            
        origin, separated = self.karaoke_separator.separate_audio_file(output_path_others)
        for stem, source in separated.items():
            if stem in ['piano', 'guitar', 'other']:
                output_path = os.path.join(output_audio_path, f'{stem}.wav')
                demucs.api.save_audio(source, output_path, samplerate=self.separator.samplerate)
        
        print(f"Succesfully separated audio. Results in {output_audio_path}")