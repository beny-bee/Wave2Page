import librosa
import numpy as np
import tensorflow as tf

# Extract features from an audio file
def extract_features_file(file_name, max_pad_len=174, n_fft=2048):
    try:
        # Load audio
        audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
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
        print("Error encountered while parsing file: ", file_name)
        return None 

