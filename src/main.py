# File: main.py

import argparse
import os


def get_tempo(audio_file):
    import librosa
    y, sr = librosa.load(audio_file, sr=None)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo

def separate_audio(input_audio_path, audio_name):
    from Splitter.Splitter import AudioSplitter
    sp = AudioSplitter()
    sp.separate(input_audio_path, audio_name)

def convert_audio_to_midi(audio_name, tempo):
    from Wav2Midi import wav2midi
    input_directory = f'data/audio_separated/{audio_name}'
    output_directory = f'data/midi/{audio_name}'

    # Create directories if they don't exist
    os.makedirs(output_directory, exist_ok=True)

    # Delete files in output_directory
    for file in os.listdir(output_directory):
        os.remove(os.path.join(output_directory, file))

    instruments = []
    for audio_file in os.listdir(input_directory):
        instrument = audio_file.split(".")[0]
        if instrument == 'other':
            continue
        input_audio_path = os.path.join(input_directory, audio_file)
        wav2midi.convert_audio_to_midi(input_audio_path, output_directory, tempo)
        instruments.append(instrument)

    midi_files = [os.path.join(output_directory, midi_file) for midi_file in os.listdir(output_directory)]
    wav2midi.combine_midi_files(midi_files, f'{output_directory}/combined.mid', instruments, tempo)

def convert_midi_to_sheet(audio_name):
    from Midi2Sheet import midi2Sheet
    input_path = f'data/midi/{audio_name}/combined.mid'
    sheet_name = f'{audio_name}'

    print(f'Converting {input_path} to sheet music...'
          f'\nOutput will be saved to {sheet_name} directory')
    midi2Sheet.midi2Sheet(input_path, sheet_name)

def main():
    parser = argparse.ArgumentParser(description='Process audio and midi files.')
    parser.add_argument('path', type=str, help='Path of the audio. Example: python3 main.py path/to/audio.mp3')
    parser.add_argument('--separate', action='store_true', help='Separate audio into tracks')
    parser.add_argument('--wav2midi', action='store_true', help='Convert audio to midi')
    parser.add_argument('--midi2sheet', action='store_true', help='Convert midi to sheet')
    
    args = parser.parse_args()

    path_array = args.path.split("/")
    audio_and_extension_name = path_array[-1]
    assert len(audio_and_extension_name.split(".")) == 2, "The audio file must have the extension .wav"
    audio_name = audio_and_extension_name.split(".")[0]
    audio_extension = audio_and_extension_name.split(".")[1]
    assert audio_extension == "wav", "The audio file must have the extension .wav"
    
    print("Audio file",args.path,"will be used")

    # Get the tempo
    tempo = round(get_tempo(args.path))
    print(f'Tempo: {tempo} BPM')

    # Separate
    if args.separate:
        separate_audio(args.path, audio_name)
    
    # Wav2Midi
    if args.wav2midi:
        convert_audio_to_midi(audio_name, tempo)

    # Midi2Sheet
    if args.midi2sheet:
        convert_midi_to_sheet(audio_name)

if __name__ == '__main__':
    main()
