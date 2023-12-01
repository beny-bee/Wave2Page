import os
from pytube import YouTube
from unidecode import unidecode
import re

def YoutubeAudioDownload(video_url, filename, path):
    video = YouTube(video_url)
    audio = video.streams.filter(only_audio = True).first()
    title = postprocess_title(video.title)
    print(title)

    try:
        out_file = audio.download(path)
        # change to .wav
        new_file = os.path.join(path, title+'.wav')
        os.rename(out_file, new_file) 
    except:
        print("Failed to download audio")

    print("Audio was downloaded successfully")
    
    return title

def postprocess_title(title):
    # Transliterate to the nearest ASCII representation
    title = unidecode(title)
    # Remove invalid file name characters
    sanitized = re.sub(r'[^\w\-_.]', '_', title)
    # Replace spaces with underscores (if any spaces left)
    sanitized = sanitized.replace(' ', '_')
    # Remove leading or trailing underscores
    sanitized = sanitized.strip('_')
    # Truncate to 250 characters to prevent filesystem errors
    sanitized = sanitized[:250]
    return sanitized

