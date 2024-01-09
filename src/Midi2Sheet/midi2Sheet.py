import os
import subprocess
from PIL import Image
from zipfile import ZipFile
    
def midi2Sheet(input_path, output_path, SEPARATOR, premium):
    # Create the output directory if it doesn't exists
    os.makedirs(output_path, exist_ok=True)
    
    # On Windows, the command is: "C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
    # On Linux Subsystem, the command is: "/mnt/c/Program Files/MuseScore 4/bin/MuseScore4.exe" or the path where is mounted from
    # On native Linux, the command is: "mscore"
    musescore_command = "/mnt/c/Program Files/MuseScore 4/bin/MuseScore4.exe"
    
    # Define the output path for the sheet music
    sheetName = output_path.split(SEPARATOR)[-2]
    outPathNoExtension = f"{output_path}{sheetName}"
    
    # MIDI file to musicxml
    # subprocess.run([musescore_command, input_path, "-o", outPathNoExtension+".xml"])
    
    # MIDI file to pdf
    # subprocess.run([musescore_command, input_path, "-o", outPathNoExtension+".pdf"])
    
    # MIDI file to png's
    subprocess.run([musescore_command, input_path, "-o", outPathNoExtension+".png"])

    path = SEPARATOR.join((outPathNoExtension+".png").split(SEPARATOR)[:-1])
    if not premium:
        for image in os.listdir(path):
            if not image.endswith(".png"): continue
            background = Image.open(path+SEPARATOR+image)
            foreground = Image.open('app/static/logos/logo_white_alpha.png')
            background = background.convert("RGBA")
            foreground = foreground.convert("RGBA")
            alpha = Image.new('L', foreground.size, 127)
            r, g, b, _ = foreground.split()
            foreground = Image.merge('RGBA', (r, g, b, alpha))
            result = Image.alpha_composite(background, foreground)
            result.save(path+SEPARATOR+image)

    with ZipFile(path+SEPARATOR+sheetName+".zip", 'w') as zip_object:
        for image in os.listdir(path):
            if not image.endswith(".png"): continue
            zip_object.write(path+SEPARATOR+image, image)