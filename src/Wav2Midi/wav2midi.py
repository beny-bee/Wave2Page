from basic_pitch.inference import predict_and_save

def convert_audio_to_midi(input_audio_path, output_directory):
    # Specify whether you want to save MIDI, audio rendering of MIDI, model outputs, and predicted note events
    save_midi = True
    sonify_midi = False
    save_model_outputs = False
    save_notes = False

    # Call the predict_and_save function to convert audio to MIDI and save the MIDI file
    predict_and_save(
        [input_audio_path],  # List of input audio file paths
        output_directory,  # Output directory to save the MIDI file
        save_midi,
        sonify_midi,
        save_model_outputs,
        save_notes
    )

