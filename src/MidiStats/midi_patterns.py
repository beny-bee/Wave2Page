import os
import pretty_midi

# Not used in the actual version

def find_midi_files(root_folder):
    for subdir, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.mid'):
                yield os.path.join(subdir, file)

midi_files = list(find_midi_files('clean_midi'))


def is_monophonic(instrument):
    # Check if the instrument plays one note at a time (useful for identifying potential vocal tracks)
    # This is a simplistic check, a more robust check might consider actual intervals and duration overlaps
    for n1, n2 in zip(instrument.notes, instrument.notes[1:]):
        if n1.end > n2.start:
            return False  # notes overlap, not monophonic
    return True

def extract_instrument_parts(midi_path):
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_path)
    except:
        print('Weird midi')
        return
    extracted_parts = {
        'piano': [],
        'guitar': [],
        'bass': [],
        'percussion': [],
        'vocals': [],  # Vocals are more nuanced, this might include various synth or ensemble sounds
    }

    for instrument in midi_data.instruments:
        if instrument.is_drum:
            extracted_parts['percussion'].append(instrument)
            continue
        
        # The program number is 0-indexed in pretty_midi but 1-indexed in the GM standard
        program = instrument.program + 1
        
        # Check for piano, guitar, bass, strings, ensemble, etc. based on program number
        if 1 <= program <= 8:
            extracted_parts['piano'].append(instrument)
        elif 25 <= program <= 32:
            extracted_parts['guitar'].append(instrument)
        elif 33 <= program <= 40:
            extracted_parts['bass'].append(instrument)
        elif 41 <= program <= 48:
            if is_monophonic(instrument):
                extracted_parts['vocals'].append(instrument)
        
    return extracted_parts

# Iterate over the MIDI files and extract parts
for midi_file in midi_files:
    parts = extract_instrument_parts(midi_file)
    if parts is None:
        continue
    print(f"Processed {midi_file}:")
    for category, instruments in parts.items():
        print(f"{category}: {len(instruments)} instruments")

