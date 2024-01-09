import os
from pytube import YouTube
from unidecode import unidecode
import re

def YoutubeAudioDownload(video_url, path):
    if (video_url != "") :
        try:
            video = YouTube(video_url)
            audio = video.streams.filter(only_audio = True).first()
            title = postprocess_title(video.title)
            out_file = audio.download(path)
            # change to .wav
            print("HERE, ",out_file)
            directory, file_name = os.path.split(out_file)
            print(directory, file_name)
            name, _ = os.path.splitext(file_name)
            print("YEEYEY", name)
            new_file_name = title + '.wav'
            new_file = os.path.join(directory, new_file_name)
            # Rename the file
            os.rename(out_file, new_file)
            # os.remove(out_file)
            print("Audio was downloaded successfully")
        except:
            print("Failed to download audio")
        
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

