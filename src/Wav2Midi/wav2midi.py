from basic_pitch.inference import predict_and_save, predict

from mido import MidiFile, MidiTrack, MetaMessage, merge_tracks
from music21 import midi, tempo, stream, instrument, note, chord, duration, pitch, interval, musicxml
import pretty_midi

import numpy as np
import partitura
import whisper
import torch
import os
from Wav2Midi.drum_model.drum2midi import drum_2_midi

def adjust_tpb(midi_file_path, new_tpb):
    midi_file = mido.MidiFile(midi_file_path)
    midi_file.ticks_per_beat = new_tpb
    return midi_file

def convert_audio_to_midi(input_audio_paths, output_directory, tempo):
    print("Converting audio to MIDI...")
    for input_audio_path in input_audio_paths:
        # Extract the instrument name from the input audio file name
        instrument_name = os.path.basename(input_audio_path).split('.')[0]

        if instrument_name == 'drums':
            continue

        # Call the predict function
        model_output, midi_data, note_events = predict(
            input_audio_path,
            midi_tempo = tempo
        )

        # Get the MIDI program for the instrument
        midi_program = instrument_name_to_program(instrument_name)

            # Change the instrument for each track in the pretty_midi object
        for instrument in midi_data.instruments:
            instrument.program = midi_program

        # Define the output MIDI file path
        output_midi_path = os.path.join(output_directory, f"{instrument_name}.mid")

        # Save the MIDI data as a MIDI file
        midi_data.write(output_midi_path)

    if 'vocals' in os.listdir(output_directory):
        pass


def convert_drums_to_midi(drum_path, output_directory, tempo):
    midi_data = drum_2_midi(drum_path, tempo)
    output_midi_path = os.path.join(output_directory, "drums.mid")
    midi_data.save(output_midi_path)


def convert_audio_to_midi_2(input_audio_paths, output_directory, tempo):
    # Specify whether you want to save MIDI, audio rendering of MIDI, model outputs, and predicted note events
    save_midi = True
    sonify_midi = False
    save_model_outputs = False
    save_notes = False

    # Call the predict_and_save function to convert audio to MIDI and save the MIDI file
    predict_and_save(
        input_audio_paths,  # List of input audio file paths
        output_directory, 
        save_midi,
        sonify_midi,
        save_model_outputs,
        save_notes,
        midi_tempo = tempo
    )


def instrument_name_to_program(instrument_name):
    if instrument_name == 'piano':
        return pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    elif instrument_name == 'vocals':
        return 52
    elif instrument_name == 'bass':
        return 33
    elif instrument_name == 'guitar':
        return 32
    elif instrument_name == 'drums':
        return 9

def combine_midi_files_manual(midi_files, output_path, instruments, tempo):
    # Create a new MIDI file to store the combined tracks
    combined_midi = MidiFile(ticks_per_beat=tempo)

    for midi_file_path, instrument in zip(midi_files, instruments):
        midi_file = MidiFile(midi_file_path)
        
        # Revise this       
        track = midi_file.tracks[1]
        time_signature_msg = None
        for msg in midi_file.tracks[0]:
            if msg.type == "time_signature":
                time_signature_msg = msg
                break
        if time_signature_msg:
            meta_track = MidiTrack([time_signature_msg])
            track = merge_tracks([track, meta_track])

        microsecs_per_beat = int(60000000 / tempo)
        meta_track = MidiTrack([MetaMessage('set_tempo', tempo=microsecs_per_beat)])
        track = merge_tracks([track, meta_track])
        track.name = instrument
        combined_midi.tracks.append(track)

    # Save the combined MIDI file
    combined_midi.save(output_path)

def combine_midi_files(midi_files, output_path, target_tempo):
    print("Combining MIDI files...")
    # Create an empty stream for the combined parts
    combined_stream = stream.Score()
    
    # Set the target tempo
    combined_stream.append(tempo.MetronomeMark(number=target_tempo))

    # Iterate over each MIDI file and corresponding intended instrument
    for midi_file_path in midi_files:
        instr_name = os.path.basename(midi_file_path).split('.')[0]
        # Load the MIDI file to a music21 stream object
        mf = midi.MidiFile()
        mf.open(midi_file_path)
        mf.read()
        mf.close()
        
        # Convert MIDI file to a music21 stream
        s = midi.translate.midiFileToStream(mf, addStartDelay=True)

        print(f"Processing {instr_name}...")
        # Process each part (track) in the MIDI

        part = s.parts[0]

        if instr_name == 'piano':
            part.quantize(quarterLengthDivisors=(4, 8), processOffsets=True, processDurations=True, inPlace=True)
        else:
            part.quantize(quarterLengthDivisors=(4,), processOffsets=True, processDurations=True, inPlace=True)

        if instr_name == 'drums':
            instr_obj = get_instrument_name_class(instr_name)
            part.insert(0, instr_obj)
            combined_stream.append(part)
            continue

        notes = [n for n in part.recurse() if isinstance(n, note.Note)]

        print(f"Found {len(notes)} notes in {instr_name}.")
        # Print out the notes and their onset

        # Clear all elements from the part (notes, rests, etc.)
        #part.clear()

        # Different quantization for piano
        #if instr_name == 'piano':
        #    #notes = quantize_notes(notes, 0.25)  # Half notes
        #    #notes = limit_note_duration(notes, 0.25)  # Limiting duration to double note (max 1 beats)
        #else:
        #    #notes = quantize_notes(notes, 0.5)  # Quarter notes

        # Apply overlapping filter for bass and vocals only
        if instr_name in ['bass', 'vocals']:
            notes = filter_overlapping_notes(notes)
            #notes = limit_note_duration(notes, 0.5)  # Limiting duration to double note (max 1 beats)

            # Find if there are chords and remove them
            chords = [n for n in part.recurse() if isinstance(n, chord.Chord)]
            if len(chords) > 0:
                print(f"Found {len(chords)} chords in {instr_name}.")
                for ch in chords:
                    part.remove(ch, recurse = True)

        if instr_name == 'piano':
            notes = remove_pitch_outliers(notes, outlier=2.5)
            notes = remove_low_velocity_notes(notes, 100)
        else:
            notes = remove_short_outliers(notes)
            notes = remove_pitch_outliers(notes)
            notes = remove_low_velocity_notes(notes)

        if instr_name in ['piano', 'guitar']:
            # Chordify the part, this will consolidate simultaneous notes into chords
            chords = [n for n in part.recurse() if isinstance(n, chord.Chord)]

            for c in chords:
                # Save original chord pitches and duration
                original_pitches = c.pitches
                duration = c.duration

                # Step 2: Remove All Notes
                for p in c.pitches:
                    c.remove(p)

                # Analyze original chord to determine quality and appropriate pitches
                original_chord = chord.Chord(original_pitches)
                root_pitch = original_chord.root()
                third_interval = interval.Interval('M3') if original_chord.quality in ['major', 'augmented'] else interval.Interval('m3')
                fifth_interval = interval.Interval('P5') if original_chord.quality not in ['diminished', 'augmented'] else interval.Interval('dim5') if original_chord.quality == 'diminished' else interval.Interval('aug5')
                seventh = None

                if original_chord.containsSeventh():
                    if original_chord.isDominantSeventh():
                        seventh = interval.Interval('m7')
                    elif original_chord.isMajorSeventh():
                        seventh = interval.Interval('M7')
                    elif original_chord.isMinorSeventh() or original_chord.isHalfDiminishedSeventh():
                        seventh = interval.Interval('m7')
                    elif original_chord.isDiminishedSeventh():
                        seventh = interval.Interval('dim7')

                # Step 3: Add Root, Third, Fifth, and possibly Seventh
                pitches_to_add = [root_pitch.transpose(i) for i in [interval.Interval('P1'), third_interval, fifth_interval] if i]  # Always add root, third, fifth

                # If the original chord had a seventh, add an appropriate seventh
                if seventh:
                    pitches_to_add.append(root_pitch.transpose(seventh))

                # Add the new notes to the chord
                for p in pitches_to_add:
                    c.add(p)

                # Restore original duration
                c.duration = duration

                c.removeRedundantPitches(inPlace=True)  # Remove duplicate pitches
                c.removeRedundantPitchClasses(inPlace=True)  # Remove duplicate pitch classes
                c.sortDiatonicAscending(inPlace=True)  # Sort the pitches in ascending order

        # Obtain the notes that should be kept
        notes_original = [n for n in part.recurse() if isinstance(n, note.Note)]
        notes_to_remove = [n for n in notes_original if n not in notes]

        for notes in notes_to_remove:
            part.remove(notes, recurse=True)

        # Get the appropriate instrument object
        instr_obj = get_instrument_name_class(instr_name)

        # If the instrument is vocals, add lyrics
        if instr_name == 'vocals':
            # Assuming transcription.txt is in the same folder as the midi file
            transcription_path = os.path.join(os.path.dirname(midi_file_path), 'transcription.txt')
            with open(transcription_path, 'r') as lyric_file:
                lyrics = lyric_file.read().split()  # Splitting words assuming each word is a note

            # Identifying the correct vocal part
            vocal_part = part
            notes_and_chords = [el for el in vocal_part.recurse() if isinstance(el, note.Note)]

            # Assign lyrics to notes and chords
            for lyric, nc in zip(lyrics, notes_and_chords):
                nc.lyric = lyric  # Assign each lyric to each note or chord

        if instr_name == 'piano':
            instr_obj.midiChannel = 1
        elif instr_name == 'bass':
            instr_obj.midiChannel = 2

        # Apply the instrument to each part and append to the combined stream
        part.insert(0, instr_obj)
                
        #part = s.parts[0]
        #part.insert(0, instr_obj)
        combined_stream.append(part)
        print()

    # Before saving, check and log the MIDI program numbers
    for i, part in enumerate(combined_stream.parts):
        pNum = part.getInstrument().midiProgram
        print(f"Part {i} Instrument: {part.getInstrument()}, MIDI Program: {pNum}")

    # Save the combined stream as a single MIDI file
    mf = midi.translate.music21ObjectToMidiFile(combined_stream)
    mf.open(output_path, 'wb')
    mf.write()
    mf.close()

    # Save the combined stream as a MusicXML file instead of a MIDI file
    xd = musicxml.m21ToXml.GeneralObjectExporter().parse(combined_stream)
    xf = open(output_path.replace('.mid', '.musicxml'), 'w')
    xf.write(xd.decode('utf-8'))
    xf.close()
    
    # mf.open(output_path.replace('.mid', '.musicxml'), 'wb')
    # mf.write()
    # mf.close()

    # combined_stream.write('musicxml', fp=output_path.replace('.mid', '.musicxml'))

def get_instrument_name_class(instrument_name):
    if instrument_name == "piano":
        return instrument.Piano()
    elif instrument_name == 'vocals':
        return instrument.Vocalist()
    elif instrument_name == 'bass':
        return instrument.ElectricBass()
    elif instrument_name == 'guitar':
        return instrument.ElectricGuitar()
    elif instrument_name == 'drums':
        return instrument.Percussion()

def transcribe_vocals(input_audio_path, output_directory):
    model = whisper.load_model("medium.en") # large
    audio = whisper.load_audio(input_audio_path)
    result = model.transcribe(audio, fp16=torch.cuda.is_available())
    text = result['text'].strip()
    with open(os.path.join(output_directory, 'transcription.txt'), 'w') as f:
        f.write(text)

    print("Transcription saved to", os.path.join(output_directory, 'transcription.txt'))

def quantize_notes(notes, quantization_step):
    """
    Quantize notes to the specified quantization level.
    """
    for n in notes:
        n.offset = round(n.offset / quantization_step) * quantization_step
        n.quarterLength = max(round(n.quarterLength / quantization_step) * quantization_step, quantization_step) # Ensure minimum length
    return notes

def limit_note_duration(notes, max_duration=1.0):
    """
    Limit the duration of notes to a maximum value.
    """
    for n in notes:
        if n.quarterLength > max_duration:
            n.quarterLength = max_duration
    return notes

def filter_overlapping_notes(notes):
    """
    Remove one of the overlapping notes in bass and vocals, favoring the one with the higher velocity.
    """
    i = 0
    while i < len(notes) - 1:
        if notes[i].offset == notes[i + 1].offset:  # if notes start at the same time
            if notes[i].volume.velocity < notes[i + 1].volume.velocity:
                del notes[i]
            else:
                del notes[i + 1]
        else:
            i += 1
    print(f"Removed {len(notes) - len(notes)} overlapping notes.")
    return notes

def remove_short_outliers(notes, octave_range=12):
    """
    Remove short duration notes that are an octave or more away from their neighbors.
    """
    cleaned_notes = []
    for i, n in enumerate(notes):
        if i > 0 and i < len(notes) - 1:  # not first or last note
            if abs(n.pitch.midi - notes[i-1].pitch.midi) > octave_range and n.quarterLength < 1:
                continue  # skip adding this note
        cleaned_notes.append(n)
    print(f"Removed {len(notes) - len(cleaned_notes)} short outlier notes.")
    return cleaned_notes

def remove_pitch_outliers(notes, outlier = 1.5):
    """
    Remove notes whose pitch is far from the median pitch and outside 2 standard deviations.
    """
    pitches = [n.pitch.midi for n in notes]  # Extract all pitches
    if len(pitches) == 0:
        return notes
    
    median_pitch = np.median(pitches)  # Calculate the median pitch
    std_pitch = np.std(pitches)  # Calculate the standard deviation of pitches

    # Define pitch boundaries
    lower_bound = median_pitch - outlier * std_pitch
    upper_bound = median_pitch + outlier * std_pitch
    # Filter notes to remove outliers
    cleaned_notes = [n for n in notes if lower_bound <= n.pitch.midi <= upper_bound]

    print(f"Removed {len(notes) - len(cleaned_notes)} outlier notes.")
    return cleaned_notes

def remove_low_velocity_notes(notes, velocity_threshold=20):
    """
    Remove notes with a velocity below the given threshold.
    """
    return [n for n in notes if n.volume.velocity > velocity_threshold]

