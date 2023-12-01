#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
from flask import Flask, render_template, redirect, request, send_from_directory, url_for, flash
from services import youtubeService as ys

DEVELOPMENT_ENV = True
PYTHONUNBUFFERED=0


import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app_data = {
    "name": "Wave2Page",
    "description": "A simple song to music sheet conversor",
    "author": "Gerard Carvaca and Armando Rodriguez and Benjami Parellada",
    "html_title": "Wave2Page",
    "project_name": "Wave2Page",
    "keywords": "wave, page, music",
}

app.config['UPLOAD_FOLDER'] = 'data/audio/'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.config['PNG_FOLDER'] = 'app/static/images/'
if not os.path.exists(app.config['PNG_FOLDER']):
    os.makedirs(app.config['PNG_FOLDER'])

app.config['WAV_FOLDER'] = 'app/static/audio/'
if not os.path.exists(app.config['WAV_FOLDER']):
    os.makedirs(app.config['WAV_FOLDER'])

@app.route("/")
def index():
    return render_template("index.html", app_data=app_data)

@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)

@app.route("/service")
def service():
    return render_template("service.html", app_data=app_data)

@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)

# @app.route('/images/<filename>')
# def serve_image(filename):
#     return send_from_directory(app.config['PNG_FOLDER']+filename.split(".")[0], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was submitted in the request
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    filename = file.filename

    if file and filename.endswith('.wav'):
        # Save the uploaded file to the upload folder
        path_to_audio = app.config['UPLOAD_FOLDER'] + filename
        file.save(path_to_audio)

        print("Calling python code")
        subprocess.call(['python3', "src/main.py", path_to_audio, "--separate", "--wav2midi", "--midi2sheet"])

        # Copy generated sheets to static folder
        png_files = []
        origin = path_to_audio.replace("audio/","sheet/").replace(".wav","")
        for f in os.listdir(origin):
            if f.endswith('.png'):
                destin = app.config['PNG_FOLDER']+f
                shutil.copyfile(origin+"/"+f, destin)
                png_files.append(destin.replace("app/",""))
        
        return render_template("index.html", filename=filename, app_data=app_data, png_files=png_files)
    else:
        return 'Invalid file format. Please upload a .wav file.'

@app.route('/upload_file_youtube', methods=['POST'])
def upload_file_youtube():
    video_url = request.form['video_url']
    title = ys.YoutubeAudioDownload(video_url, app.config['UPLOAD_FOLDER'])
    flash("Succesfuly dowloaded audio from youtube!")  # Flashing the success or error message
    
    path_to_audio = app.config['UPLOAD_FOLDER'] + title + '.wav'
    print('PATH:', path_to_audio)
    flash("System working on sheet generation...")
    subprocess.call(['python3', "src/main.py", path_to_audio, "--separate", "--wav2midi", "--midi2sheet"])
    flash(title+" - Succesful!")
    
    # Copy generated sheets to static folder
    png_files = []
    origin = path_to_audio.replace("audio/","sheet/").replace(".wav","")
    for f in os.listdir(origin):
        if f.endswith('.png'):
            destin = app.config['PNG_FOLDER']+f
            shutil.copyfile(origin+"/"+f, destin)
            png_files.append(destin.replace("app/",""))
    
    return render_template("service.html", filename=filename, app_data=app_data, png_files=png_files)

@app.route('/tracks_volume', methods=['POST'])
def tracks_volume():
    filename = request.form['filename']
    path_to_audio = app.config['UPLOAD_FOLDER'] + filename
    path_to_audios_separated = path_to_audio.replace("audio/","separated/")

    audio_files = []
    destin_folder = app.config['WAV_FOLDER'] + filename + "/"
    if not os.path.exists(destin_folder):
        os.makedirs(destin_folder)
    for f in os.listdir(path_to_audios_separated):
        if f.endswith('.wav'):
            destin = destin_folder + f
            shutil.copyfile(path_to_audios_separated+"/"+f, destin)
            audio_files.append(destin.replace("app/",""))

    audio_files = [file.replace("app/","") for file in audio_files]
    return render_template("service.html", app_data=app_data, audio_files=audio_files)

if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)
