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

    
def midi2Sheet_2(input_path, output_path, SEPARATOR, premium):
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
    # subprocess.run([musescore_command, input_path, "-o", outPath])
    
    # Apply changes to musicxml
    # modifyMusicXML(outPath)
    
    # Run MuseScore to convert the MIDI file to sheet music
    ###### I think is not taking the styles form there ######
    # subprocess.run([musescore_command, input_path, "-o", outPathNoExtension+".pdf"])

    # Add logo to pdf
    # addLogoToPDF(outPathNoExtension+".pdf", outPathNoExtension+".pdf",
    #              'app/static/logos/logo_white.png')
    
    subprocess.run([musescore_command, input_path, "-o", outPathNoExtension+".png"])

    if not premium:
        path = SEPARATOR.join((outPathNoExtension+".png").split(SEPARATOR)[:-1])
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

def addLogoToPDF2(input_pdf_path, output_pdf_path, logo_path):
    with open(input_pdf_path, 'rb') as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            width = 150
            height = 150
            x_position = int((page.mediabox[2] - page.mediabox[0] - width) / 2)
            y_position = int((page.mediabox[3] - page.mediabox[1] - height) / 2)
            can.drawImage(logo_path, x_position, y_position, width=width, height=height, mask=[0,2,40,42,136,139])
            can.save()
            packet.seek(0)
            overlay = PyPDF2.PdfReader(packet)
            page.merge_page(overlay.pages[0])
            pdf_writer.add_page(page)
        with open(output_pdf_path, 'wb') as output_pdf_file:
            pdf_writer.write(output_pdf_file)

import fitz  # PyMuPDF
from PyPDF2 import PageObject
# from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image

def addLogoToPDF(input_pdf_path, output_pdf_path, logo_path):
    # with open(input_pdf_path, 'rb') as input_pdf_file:
    # pdf_reader = PyPDF2.PdfReader(input_pdf_file)
    pdf_writer = PyPDF2.PdfWriter()
    # Create a PDF writer object
    # pdf_writer = PdfFileWriter()

    # Read the existing PDF
    existing_pdf = PyPDF2.PdfReader(open(input_pdf_path, "rb"))

    # logoPdf = PyPDF2.PdfReader(open("data/sheet/name.pdf", "rb"))
    # logoPdf_image = fitz.Pixmap(logoPdf)

    for page_number in range(len(existing_pdf.pages)):
        pdf_page = existing_pdf.pages[page_number]


        pdf_page_image = pdf_page.get_pixmap()

        background_image = Image.open(logo_path)

        background_image = background_image.resize((pdf_page_image.width, pdf_page_image.height))

        # Merge the background image and PDF page with alpha
        blended_image = Image.blend(background_image, pdf_page_image, alpha=0.5)

        # Create a new PDF page from the blended image
        new_pdf_page = fitz.open()
        new_pdf_page.new_page(width=pdf_page.rect.width, height=pdf_page.rect.height)
        new_pdf_page[-1].insert_pixmap(fitz.Rect(0, 0, pdf_page.rect.width, pdf_page.rect.height), pixmap=blended_image)

        # Add the new page to the PDF writer
        pdf_writer.addPage(new_pdf_page[-1])


        # doc = fitz.open(input_pdf_path)
        # page = doc[page_number]

        # # Get the size of the page
        # width, height = page.rect.width, page.rect.height

        # # Create a new page with the same dimensions
        # new_page = PageObject.create_blank_page(width, height)

        # # Merge the existing PDF content onto the new page
        # new_page.mergeTranslatedPage(page, 0, 0)

        # # Add the image with alpha 0.5 as a background
        # image = fitz.Image(logo_path)
        # image.set_opacity(0.5)
        # new_page.insertImage(page.rect, pixmap=image)

        # # Add the new page to the PDF writer
        # pdf_writer.addPage(new_page)

        # packet = BytesIO()
        # can = canvas.Canvas(packet, pagesize=A4)
        # width = 150
        # height = 150
        # x_position = int((page.mediabox[2] - page.mediabox[0] - width) / 2)
        # y_position = int((page.mediabox[3] - page.mediabox[1] - height) / 2)
        # can.drawImage(logo_path, x_position, y_position, width=width, height=height, mask=[0,2,40,42,136,139])
        # can.save()
        # packet.seek(0)
        # overlay = PyPDF2.PdfReader(packet)
        # page.merge_page(overlay.pages[0])

    with open(output_pdf_path, 'wb') as output_pdf_file:
        pdf_writer.write(output_pdf_file)