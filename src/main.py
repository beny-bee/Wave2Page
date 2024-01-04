import os
import librosa
import argparse
from music21 import midi
from Wav2Midi import wav2midi
from Midi2Sheet import midi2Sheet
import utils

#from Splitter.Splitter import AudioSplitter

SEPARATOR = "\\" if os.name == 'nt' else "/"

def get_tempo(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo

def separate_audio(input_path, output_path, instruments):
    sp = AudioSplitter(SEPARATOR, instruments)
    sp.separate(input_path, output_path)

def convert_audio_to_midi(input_path, output_path, tempo):
    # Create directories if they don't exist
    os.makedirs(output_path, exist_ok=True)

    # Delete files in output_directory
    for file in os.listdir(output_path):
        os.remove(os.path.join(output_path, file))

    instruments = []
    audio_paths = []

    for audio_file in os.listdir(input_path):
        instrument = audio_file.split(".")[0]
        if instrument == 'other':
            continue
        input_audio_path = os.path.join(input_path, audio_file)
        if utils.is_audio_silent(input_audio_path):
            continue
        if instrument == 'vocals':
            wav2midi.transcribe_vocals(input_audio_path, output_path)
        audio_paths.append(input_audio_path)
        instruments.append(instrument)

    wav2midi.convert_audio_to_midi(audio_paths, output_path, tempo)
    if 'drums' in instruments:
        audio_path_drum = [audio_path for audio_path in audio_paths if audio_path.split(SEPARATOR)[-1].split(".")[0] == 'drums'][0]
        wav2midi.convert_drums_to_midi(audio_path_drum, output_path, tempo)

    midi_files = [os.path.join(output_path, midi_file) for midi_file in os.listdir(output_path) if midi_file.endswith(".mid")]
    midi_files = sorted(midi_files, key=utils.sort_paths)
    wav2midi.combine_midi_files(midi_files, f'{output_path}{SEPARATOR}combined.mid', tempo)
    #wav2midi.combine_midi_files(midi_files, f'{output_path}{SEPARATOR}combined.mid', instruments, tempo)
       
def convert_midi_to_sheet(input_path, output_path):
    output_path = output_path if output_path[-1] == SEPARATOR else output_path + SEPARATOR
    print(f'Converting {input_path} to sheet music...\nOutput will be saved to {output_path} directory')
    midi2Sheet.midi2Sheet(f"{input_path}{SEPARATOR}combined.mid", output_path, SEPARATOR)

def main():
    parser = argparse.ArgumentParser(description='Process audio and midi files to generate music sheeets.')
    parser.add_argument('input_path', type=str, help='Path of the audio for the first process. Example: python3 main.py path/to/audio.mp3')
    parser.add_argument('--separate', action='store_true', help='Separate audio into tracks')
    parser.add_argument('--instruments', action='store', type=str, help='Instruments to be used in the separation process', required=False)
    parser.add_argument('--wav2midi', action='store_true', help='Convert audio to midi')
    parser.add_argument('--midi2sheet', action='store_true', help='Convert midi to sheet')

    args = parser.parse_args()
    input_path_original = args.input_path
    input_path = args.input_path

    instruments = args.instruments.split(",") if args.instruments else None

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
        separate_audio(input_path, output_path, instruments)
    
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
