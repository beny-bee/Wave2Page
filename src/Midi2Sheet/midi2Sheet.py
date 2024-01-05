import os
import PyPDF2
import warnings
import subprocess
import partitura as pt
from io import BytesIO
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


#warnings.filterwarnings("ignore", category=UserWarning)

# def midi2Sheet1(input_path, output_path, SEPARATOR):    
#     # Create the output directory if it doesn't exists
#     os.makedirs(output_path, exist_ok=True)
    
#     # Load score
#     score = pt.load_score(input_path)
    
#     sheetName = output_path.split(SEPARATOR)[-2]
#     for i, part in enumerate(score.parts):
#         outPath = f"{output_path}{SEPARATOR}{sheetName}_{part.part_name}.png"
#         pt.display.render_musescore(part, fmt="png", out=outPath)
#         print(f"Done {i+1}/{len(score.parts)}")

def midi2Sheet(input_path, output_path, SEPARATOR):
    os.makedirs(output_path, exist_ok=True)
    
    # Load the MIDI file as a Part object
    part = pt.load_score(input_path).parts[0]
    print(part.pretty())
    pt.render(part)

    
def midi2Sheet_2(input_path, output_path, SEPARATOR):
    # Create the output directory if it doesn't exists
    os.makedirs(output_path, exist_ok=True)
    
    # On Windows, the command is: "C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
    # On Linux Subsystem, the command is: "/mnt/c/Program Files/MuseScore 4/bin/MuseScore4.exe" or the path where is mounted from
    # On native Linux, the command is: "mscore"
    musescore_command = "/mnt/c/Program Files/MuseScore 4/bin/MuseScore4.exe"
    
    # Define the output path for the sheet music
    sheetName = output_path.split(SEPARATOR)[-2]
    outPathNoExtension = f"{output_path}{sheetName}"
    outPath = outPathNoExtension+".xml"
    
    # Run MuseScore to convert the MIDI file to musicxml
    subprocess.run([musescore_command, input_path.replace("musicxml","mid"), "-o", outPath])
    
    # Apply changes to musicxml
    # modifyMusicXML(outPath)
    
    # Run MuseScore to convert the MIDI file to sheet music
    ###### I think is not taking the styles form there ######
    subprocess.run([musescore_command, input_path, "-o", outPathNoExtension+".pdf", "--style", SEPARATOR.join(["data","sheet","style.mss"])])
    # subprocess.run([musescore_command, outPath, "-o", outPathNoExtension+".png", "-f"])
    
    # Add logo to pdf
    addLogoToPDF(outPathNoExtension+".pdf", outPathNoExtension+".pdf",
                 'app/static/logos/logo_white.png', x_position=475, y_position=750)
    
    
def modifyMusicXML(path):
    with open(path, 'r') as f:
        data = f.read()
    
    data = BeautifulSoup(data, "xml")
    scoreData = data.find("score-partwise")
    partsInfo = scoreData.find("part-list").find_all("score-part")
    
    for partInfoIdx in range(len(partsInfo)):
        aux = partsInfo[partInfoIdx].find("part-name")
        instrument = aux.string.split(", ")[-1].capitalize()
        aux.string = instrument
        aux = partsInfo[partInfoIdx].find("part-abbreviation")
        aux.string = instrument
        aux = partsInfo[partInfoIdx].find("score-instrument").find("instrument-name")
        aux.string = instrument
    
    f = open(path, "wb")
    f.write(data.encode('utf-8'))
    f.close()
    print("Done applying modifications to musicXML.", end="")

def addLogoToPDF(input_pdf_path, output_pdf_path, logo_path, x_position, y_position):
    with open(input_pdf_path, 'rb') as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            if page_number == 0:
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)
                can.drawImage(logo_path, x_position, y_position, width=75, height=75)
                can.save()
                packet.seek(0)
                overlay = PyPDF2.PdfReader(packet)
                page.merge_page(overlay.pages[0])
            pdf_writer.add_page(page)
        with open(output_pdf_path, 'wb') as output_pdf_file:
            pdf_writer.write(output_pdf_file)