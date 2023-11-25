import os
from pytube import YouTube

def YoutubeAudioDownload(video_url, filename, path):
    video = YouTube(video_url)
    audio = video.streams.filter(only_audio = True).first()

    try:
        out_file = audio.download(path)
        # change to .wav
        new_file = os.path.join(path, filename+'.wav')
        os.rename(out_file, new_file) 
    except:
        print("Failed to download audio")

    print("Audio was downloaded successfully")