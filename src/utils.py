import os
import librosa
import numpy as np
import tensorflow as tf


def is_audio_silent(input_audio_path, silence_threshold=-40.0, silence_ratio=0.95):
    # Skip if it's not an audio file
    if not input_audio_path.lower().endswith(('.wav', '.mp3', '.flac', '.aiff')):
        print("Invalid audio file format.")
        return False

    # Load audio file
    y, sr = librosa.load(input_audio_path, sr=None)

    # Convert to amplitude and then to dB
    amplitude = np.abs(y)
    amplitude_db = librosa.amplitude_to_db(amplitude)

    # Calculate the duration of silence
    silence = amplitude_db < silence_threshold
    silence_duration = np.sum(silence) / sr  # Duration in seconds

    # Calculate the total duration of the file
    total_duration = len(y) / sr

    # Calculate ratio of silence duration to total duration
    silence_ratio_in_file = silence_duration / total_duration

    # Check if silent duration is less than the allowed ratio
    if silence_ratio_in_file < silence_ratio:
        print(f"File {os.path.basename(input_audio_path)} has acceptable silence ratio.")
        return False
    else:
        print(f"File {os.path.basename(input_audio_path)} is predominantly silent.")
        return True
    
# Function to extract instrument name from the file path
def sort_paths(path, instrument_order = ['vocals', 'piano', 'guitar', 'bass', 'drums']):
    for i, instrument in enumerate(instrument_order):
        if instrument in path:
            return i
    return len(instrument_order)