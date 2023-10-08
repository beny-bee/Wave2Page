from basic_pitch.inference import predict_and_save


import mido
from mido import MidiFile, MidiTrack, Message

def convert_audio_to_midi(input_audio_path, output_directory):
    # Specify whether you want to save MIDI, audio rendering of MIDI, model outputs, and predicted note events
    save_midi = True
    sonify_midi = False
    save_model_outputs = False
    save_notes = False

    # Call the predict_and_save function to convert audio to MIDI and save the MIDI file
    predict_and_save(
        [input_audio_path],  # List of input audio file paths
        output_directory, 
        save_midi,
        sonify_midi,
        save_model_outputs,
        save_notes
    )

def combine_midi_files(midi_files, output_path, instruments):
    # Create a new MIDI file to store the combined tracks
    combined_midi = MidiFile()

    for midi_file_path, instrument in zip(midi_files,instruments):
        midi_file = MidiFile(midi_file_path)
        for track in midi_file.tracks:
            track.name = instrument
            combined_midi.tracks.append(track)

    # Save the combined MIDI file
    combined_midi.save(output_path)