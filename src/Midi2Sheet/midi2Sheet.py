import os
import warnings
import partitura as pt
import subprocess

#warnings.filterwarnings("ignore", category=UserWarning)

# def midi2Sheet(midiPath, sheetName, mode="pdf"):
#     assert mode in ["pdf", "png"], "mode must be pdf or png"
#     score = pt.load_score(midiPath)
#     os.makedirs(f'data/sheet/{sheetName}', exist_ok=True)
#     for i, part in enumerate(score.parts):
#         outPath = f"data/sheet/{sheetName}/{sheetName}_{part.part_name}.{mode}"
#         print(outPath)
#         pt.display.render_musescore(part, fmt=mode, out=outPath)
#         print(f"Done {i+1}/{len(score.parts)}", end="\r")


def midi2Sheet(input_path, output_path, SEPARATOR, mode="pdf"):
    assert mode in ["pdf", "png"], "mode must be pdf or png"
    
    # Create the output directory if it doesn't exists
    os.makedirs(output_path, exist_ok=True)
    
    # On Windows, the command might be r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
    musescore_command = pt.io.musescore.find_musescore() #"mscore" for benja
    
    sheetName = output_path.split(SEPARATOR)[-2]
    # Define the output path for the sheet music
    outPath = f"{output_path}{SEPARATOR}{sheetName}.{mode}"
    
    # Run MuseScore to convert the MIDI file to sheet music
    subprocess.run([musescore_command, input_path, "-o", outPath]) #"--score-mp3"