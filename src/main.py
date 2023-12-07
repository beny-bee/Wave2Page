import os
import librosa
import argparse
from music21 import midi
from Wav2Midi import wav2midi
from Midi2Sheet import midi2Sheet
from Splitter.Splitter import AudioSplitter

SEPARATOR = "\\" if os.name == 'nt' else "/"

def get_tempo(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo

def separate_audio(input_path, output_path):
    sp = AudioSplitter(SEPARATOR)
    sp.separate(input_path, output_path)

def convert_audio_to_midi(input_path, output_path, tempo):
    # Create directories if they don't exist
    os.makedirs(output_path, exist_ok=True)

    # Delete files in output_directory
    for file in os.listdir(output_path):
        os.remove(os.path.join(output_path, file))

    instruments = []
    for audio_file in os.listdir(input_path):
        instrument = audio_file.split(".")[0]
        if instrument == 'other':
            continue
        input_audio_path = os.path.join(input_path, audio_file)
        wav2midi.convert_audio_to_midi(input_audio_path, output_path, tempo)
        instruments.append(instrument)

    midi_files = [os.path.join(output_path, midi_file) for midi_file in os.listdir(output_path)]
    wav2midi.combine_midi_files(midi_files, f'{output_path}{SEPARATOR}combined.mid', instruments, tempo)
    
#     aux_midi = midi.MidiFile()
#     aux_midi.open(f'{output_directory}/combined.mid', "rb")
#     aux_midi.read()
#     aux_midi.close()
#     print(aux_midi.tracks)
#     for t in aux_midi.tracks:
#         for e in [t.events[0]]:
#             print(e.type)
#     # aux_midi = midi.translate.midiFilePathToStream(f'{output_directory}/combined.mid')
#     parts = aux_midi.parts
#     for part,instrument in zip(parts,instruments):
#         print(part.partName)
#         part.partName = instrument
#         print(part.partName)
#     aux_midi = midi.translate.streamToMidiFile(aux_midi)
#     aux_midi.open(f'{output_directory}/combined.mid', "wb")
#     aux_midi.write()
#     aux_midi.close()
            

def convert_midi_to_sheet(input_path, output_path):
    output_path = output_path if output_path[-1] == SEPARATOR else output_path + SEPARATOR
    print(f'Converting {input_path} to sheet music...\nOutput will be saved to {output_path} directory')
    midi2Sheet.midi2Sheet(f"{input_path}{SEPARATOR}combined.mid", output_path, SEPARATOR)

def main():
    parser = argparse.ArgumentParser(description='Process audio and midi files to generate music sheeets.')
    parser.add_argument('input_path', type=str, help='Path of the audio for the first process. Example: python3 main.py path/to/audio.mp3')
    parser.add_argument('--separate', action='store_true', help='Separate audio into tracks')
    parser.add_argument('--wav2midi', action='store_true', help='Convert audio to midi')
    parser.add_argument('--midi2sheet', action='store_true', help='Convert midi to sheet')

    args = parser.parse_args()
    input_path_original = args.input_path
    input_path = args.input_path

    if args.separate:
        assert input_path_original.startswith(f"data{SEPARATOR}audio"), f"The path '{input_path_original}' when using --separate should start with data{SEPARATOR}audio"
        audio_and_extension_name = input_path_original.split(SEPARATOR)[-1].split(".")
        assert len(audio_and_extension_name) == 2, "The audio file must have the extension .wav"
        assert audio_and_extension_name[1] == "wav", "The audio file must have the extension .wav"
    elif args.wav2midi:
        assert input_path_original.startswith(f"data{SEPARATOR}separated"), f"The path '{input_path_original}' when using --wav2midi should start with data{SEPARATOR}separated"
        assert input_path_original.split(SEPARATOR)[-1] == "", f"The path '{input_path_original}' should be a directory when using --wav2midi. End the path with {SEPARATOR}"
    elif args.midi2sheet:
        assert input_path_original.startswith(f"data{SEPARATOR}midi"), f"The path '{input_path_original}' when using --midi2sheet should start with data{SEPARATOR}midi"
        assert input_path_original.split(SEPARATOR)[-1] == "", f"The path '{input_path_original}' should be a directory when using --midi2sheet. End the path with {SEPARATOR}"
    
    print(f"Audio file from {input_path_original} will be used")

    # Get the tempo
    tempo = round(get_tempo(input_path_original)) if args.separate else 120
    print(f"Tempo: {tempo} BPM ({'Calculated' if args.separate else 'Default'})")

    # Separate
    if args.separate:
        output_path = input_path_original.replace(f"data{SEPARATOR}audio",f"data{SEPARATOR}separated").replace(".wav","")
        separate_audio(input_path, output_path)
    
    # Wav2Midi
    if args.wav2midi:
        if args.separate:
            input_path = input_path.replace(f"data{SEPARATOR}audio",f"data{SEPARATOR}separated").replace(".wav","")
            output_path = input_path_original.replace(f"data{SEPARATOR}audio",f"data{SEPARATOR}midi").replace(".wav","")
        else:
            output_path = input_path_original.replace(f"data{SEPARATOR}separated",f"data{SEPARATOR}midi").replace(".wav","")
        convert_audio_to_midi(input_path, output_path, tempo)
        
    # Midi2Sheet
    if args.midi2sheet:
        output_path = input_path_original.replace(f"data{SEPARATOR}midi",f"data{SEPARATOR}sheet").replace(".wav","")
        if args.separate:
            if not args.wav2midi:
                input_path = input_path.replace(f"data{SEPARATOR}audio",f"data{SEPARATOR}midi")
            else:
                input_path = input_path.replace(f"data{SEPARATOR}separated",f"data{SEPARATOR}midi")
            output_path = input_path_original.replace(f"data{SEPARATOR}audio",f"data{SEPARATOR}sheet").replace(".wav","")
        elif args.wav2midi:
            input_path = input_path.replace(f"data{SEPARATOR}separated",f"data{SEPARATOR}midi")
            output_path = input_path_original.replace(f"data{SEPARATOR}separated",f"data{SEPARATOR}sheet").replace(".wav","")
        convert_midi_to_sheet(input_path, output_path)

if __name__ == '__main__':
    main()
