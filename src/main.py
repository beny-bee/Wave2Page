# File: main.py

import argparse
import os
from Midi2Sheet import midi2Sheet
from Wav2Midi import wav2midi
from splitter.Splitter import AudioSplitter

def separate_audio(input_audio_path, audio_name):
    sp = AudioSplitter()
    sp.separate(input_audio_path, audio_name)

def convert_audio_to_midi(audio_name):
    input_directory = f'data/audio_separated/{audio_name}'
    output_directory = f'data/midi/{audio_name}'

    # Create directories if they don't exist
    os.makedirs(output_directory, exist_ok=True)

    instruments = []
    for audio_file in os.listdir(input_directory):
        input_audio_path = os.path.join(input_directory, audio_file)
        wav2midi.convert_audio_to_midi(input_audio_path, output_directory)
        instruments.append(audio_file.split(".")[0])

    midi_files = [os.path.join(output_directory, midi_file) for midi_file in os.listdir(output_directory)]
    wav2midi.combine_midi_files(midi_files, f'{output_directory}/combined.mid', instruments)

def convert_midi_to_sheet(audio_name):
    input_path = f'data/midi/{audio_name}/combined.mid'
    sheet_name = f'{audio_name}'

    print(f'Converting {input_path} to sheet music...'
          f'\nOutput will be saved to {sheet_name} directory')
    midi2Sheet.midi2Sheet(input_path, sheet_name)

def main():
    parser = argparse.ArgumentParser(description='Process audio and midi files.')
    parser.add_argument('--separate', action='store_true', help='Separate audio into tracks')
    parser.add_argument('--wav2midi', action='store_true', help='Convert audio to midi')
    parser.add_argument('--midi2sheet', action='store_true', help='Convert midi to sheet')

    args = parser.parse_args()

    audio_name = 'audio_example'

    if args.separate:
        input_audio_path = f'data/audio/{audio_name}.mp3'
        separate_audio(input_audio_path, audio_name)
    if args.wav2midi:
        convert_audio_to_midi(audio_name)
    if args.midi2sheet:
        convert_midi_to_sheet(audio_name)

if __name__ == '__main__':
    main()
