import argparse
from midi2Sheet import midi2Sheet
from Wav2Midi import wav2midi

def convert_audio_to_midi(input_audio_path, output_directory):
    wav2midi.convert_audio_to_midi(input_audio_path, output_directory)

def convert_midi_to_sheet(midi_path, sheet_name):
    midi2Sheet.midi2Sheet(midi_path, sheet_name)

def main():
    parser = argparse.ArgumentParser(description='Process audio and midi files.')
    parser.add_argument('--wav2midi', action='store_true', help='Convert audio to midi')
    parser.add_argument('--midi2sheet', action='store_true', help='Convert midi to sheet')

    args = parser.parse_args()

    # Specify the path to your audio file and the directory where you want to save the MIDI file
    input_audio_path = 'src/Wav2Midi/test/examples/audio_example.mp3'
    output_directory = 'src/Wav2Midi/test/Midi'

    midi_path = "midi2Sheet/SampleMIDI.mid"
    sheet_name = "FirstMusicSheets"

    if args.wav2midi:
        convert_audio_to_midi(input_audio_path, output_directory)
    if args.midi2sheet:
        convert_midi_to_sheet(midi_path, sheet_name)

if __name__ == '__main__':
    main()
