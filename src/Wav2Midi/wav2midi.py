from basic_pitch.inference import predict_and_save

from mido import MidiFile, MidiTrack, MetaMessage

def adjust_tpb(midi_file_path, new_tpb):
    midi_file = mido.MidiFile(midi_file_path)
    midi_file.ticks_per_beat = new_tpb
    return midi_file

def convert_audio_to_midi(input_audio_path, output_directory, tempo):
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
        save_notes,
        midi_tempo = tempo
    )

def combine_midi_files(midi_files, output_path, instruments, tempo):
    # Create a new MIDI file to store the combined tracks
    combined_midi = MidiFile(ticks_per_beat=220)

    # Create a new track for meta messages
    meta_track = MidiTrack()
    # Convert the tempo from BPM to microseconds per beat (the standard MIDI format for tempo)
    microsecs_per_beat = int(60000000 / tempo)
    # Append a set_tempo meta message with the specified tempo
    meta_track.append(MetaMessage('set_tempo', tempo=microsecs_per_beat))
    # Append the meta track to the combined MIDI file
    combined_midi.tracks.append(meta_track)

    for midi_file_path, instrument in zip(midi_files, instruments):
        midi_file = MidiFile(midi_file_path)
        for track in midi_file.tracks:
            track.name = instrument
            combined_midi.tracks.append(track)


    # Save the combined MIDI file
    combined_midi.save(output_path)