import os
import mido
import sounddevice as sd
from midi2audio import FluidSynth
import numpy as np
from scipy.io.wavfile import read

midi_dir = 'data/midi/audio_example/'
wav_dir = 'data/separated/audio_example/'
sf2_path = 'WiiGrandPiano.sf2'

# Comparacio midi amd wav
# compte quan pasa a mono pot petar les orelles lmao

fs = FluidSynth(sound_font=sf2_path)

for wav_file in os.listdir(wav_dir):
    if wav_file.endswith('.wav'):
        wav_path = os.path.join(wav_dir, wav_file)
        midi_path = os.path.join(midi_dir, wav_file.replace('.wav', '.mid'))

        print('File:', wav_path)
        print('MIDI Path:', midi_path)

        # Synthesize MIDI to audio using FluidSynth
        output_audio_path = 'output.wav'  # Temporary output file
        fs.midi_to_audio(midi_path, output_audio_path)

        # Read the generated audio file
        sample_rate, generated_audio = read(output_audio_path)

        # Read the original audio file for comparison
        sample_rate, wav_audio = read(wav_path)

        min_length = min(len(generated_audio), len(wav_audio))
        generated_audio = generated_audio[:min_length]
        wav_audio = wav_audio[:min_length]

        print("Generated audio shape:", generated_audio.shape)
        print("WAV audio shape:", wav_audio.shape)

        # Handle stereo and mono cases
        if generated_audio.ndim == 2 and wav_audio.ndim == 1:  # If stereo
            generated_audio = np.mean(generated_audio, axis=1)  # Convert to mono by averaging channels

        mixed_audio = generated_audio + wav_audio

        # Play the combination
        sd.play(mixed_audio, samplerate=44100, blocking=True)