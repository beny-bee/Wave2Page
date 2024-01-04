import librosa
import mido
from mido import Message, MidiFile, MidiTrack
import random
import os
import soundfile as sf
import tensorflow as tf
import numpy as np
import sys

# Your specific drum types
DRUM_TYPES = ['hat', 'tom', 'ride', 'open', 'kick', 'bongo', 'clap', 'snare', 'rim', 'snap', 'crash', 'shaker']

# A mapping from your class names to MIDI note numbers
note_mapping = {
    'hat': 42,  # Closed Hi Hat
    'tom': 45,  # Low Tom or another tom note
    'ride': 51,  # Ride Cymbal 1
    'open': 46,  # Open Hi-Hat
    'kick': 36,  # Bass Drum 1
    'bongo': 60,  # Hi Bongo
    'clap': 39,  # Hand Clap
    'snare': 38,  # Acoustic Snare
    'rim': 37,  # Side Stick
    'snap': 40,  # Electric Snare
    'crash': 49,  # Crash Cymbal 1
    'shaker': 70  # Maracas
}

def extract_features(audio, sample_rate, max_pad_len=174, n_fft=2048):
    try:
        if len(audio) < n_fft:  # Padding short files
            audio = np.pad(audio, (0, max(0, n_fft - len(audio))), "constant")
            
        # Extracting features
        features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        #centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
        #rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)
        #zcr = librosa.feature.zero_crossing_rate(audio)
        
        # Concatenate all features into one numpy array
        #features = np.concatenate((mfccs, centroid, rolloff, zcr), axis=0)

        # Padding
        pad_width = max_pad_len - features.shape[1]
        features = np.pad(features, pad_width=((0, 0), (0, pad_width)), mode='constant')

        return features
        
    except Exception as e:
        print("Error encountered while parsing audio data")
        return None 
    
# Classify each onset (just randomly for now)
def model_classify(audio_clip, model, sr=44100, top_n=2, threshold_diff=0.1):
    # Extract features or preprocess audio_clip
    features = extract_features(audio_clip, sr)
    # Make prediction using the model
    features = np.expand_dims(features, axis=0)
    prediction = model.predict(features)

    # Get top N predictions
    top_n_predictions = prediction[0].argsort()[-top_n:][::-1]
    top_n_probabilities = prediction[0][top_n_predictions]

    # Check if top predictions are close
    if (top_n_probabilities[0] - top_n_probabilities[-1]) < threshold_diff:
        return top_n_predictions  # Return all top N predictions
    return [top_n_predictions[0]]  # Return only the top prediction

def drum_2_midi(audio_path, bpm=120, top_n=3):
    # Load the audio file
    #audio_path = '../data/separated/audio_example/drums.wav'

    y, sr = librosa.load(audio_path)
    model = tf.keras.models.load_model('src/Wav2Midi/drum_model/drum_model.keras')

    # Detect onsets
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    # Convert onset frames to time
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
    # Convert to MIDI
    midi_file = MidiFile()
    track = MidiTrack()
    midi_file.tracks.append(track)

    ticks_per_beat = midi_file.ticks_per_beat  # default is generally 480

    # Setting up the tempo (microseconds per beat)
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))

    # Initialize a variable to keep track of the previous onset time in ticks
    prev_onset_tick = 0

    # Define note length in beats (0.25 for quarter note, 0.5 for half note, etc.)
    note_length_in_beats = 0.25  # quarter note

    # Predict and create MIDI notes for each onset
    for i, onset_time in enumerate(onset_times):
        start_sample = int(onset_time * sr)
        # Define end_sample for the clip based on next onset or a fixed duration
        end_sample = start_sample + int(0.5 * sr)  # 0.5 second clip or as per your preference
        clip = y[start_sample:end_sample]  # extract the audio clip

        # Extract features and predict top N hits
        predicted_labels = model_classify(clip, model, sr, top_n=top_n)
        if not predicted_labels:
            continue

        onset_tick = int(onset_time * ticks_per_beat * bpm / 60)
        delta_ticks = onset_tick - prev_onset_tick
        note_length_ticks = int(note_length_in_beats * ticks_per_beat)  # calculate note length in ticks

        # Create MIDI note events for each predicted label
        for label in predicted_labels:
            note = note_mapping[DRUM_TYPES[label]]
            # Add MIDI note on event
            track.append(Message('note_on', note=note, velocity=64, time=delta_ticks, channel=9))
            # Instead of adding note_off immediately after, add it after 'note_length_ticks'
            track.append(Message('note_off', note=note, velocity=64, time=note_length_ticks, channel=9))

        prev_onset_tick = onset_tick

    # Clean tensorflow session
    tf.keras.backend.clear_session()

    # Save the MIDI file
    #midi_file.save('predicted_drums.mid')
    return midi_file
