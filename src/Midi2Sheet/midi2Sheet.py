import os
import warnings
import partitura as pt

warnings.filterwarnings("ignore", category=UserWarning)

def midi2Sheet(midiPath, sheetName, mode="pdf"):
    assert mode in ["pdf", "png"], "mode must be pdf or png"
    score = pt.load_score(midiPath)
    os.makedirs(f'../data/sheet/{sheetName}', exist_ok=True)
    for i, part in enumerate(score.parts):
        outPath = f"../data/sheet/{sheetName}/{sheetName}_{part.part_name}.{mode}"
        pt.display.render_musescore(part, fmt=mode, out=outPath) # Need MuseScore
