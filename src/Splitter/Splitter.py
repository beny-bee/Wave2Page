import demucs.api
import os

class AudioSplitter:

    def __init__(self):
        self.separator = demucs.api.Separator(model="htdemucs_6s", progress=True)
        self.piano_improver = demucs.api.Separator(model="htdemucs_6s")

    def separate(self, input_audio_path, audio_name):
        print('Separating audio sources...')
        origin, separated = self.separator.separate_audio_file(input_audio_path)
        
        # Define the output directory for the separated audio files
        output_directory = f'data/audio_separated/{audio_name}'
        os.makedirs(output_directory, exist_ok=True)
        
        for stem, source in separated.items():
            output_path = os.path.join(output_directory, f'{stem}.wav')
            demucs.api.save_audio(source, output_path, samplerate=self.separator.samplerate)

        print(f"Succesfully separated track: {audio_name} - results in {output_directory}")