import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO


def addLogoToPDF2(input_pdf_path, output_pdf_path, logo_path):
    with open(input_pdf_path, 'rb') as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        page = pdf_reader.pages[0]
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        width = 600
        height = 600
        x_position = int((page.mediabox[2] - page.mediabox[0] - width) / 2)
        y_position = int((page.mediabox[3] - page.mediabox[1] - height) / 2)
        can.drawImage(logo_path, x_position, y_position, width=width, height=height, mask='auto')
        can.save()
        packet.seek(0)
        packet.seek(0)
        overlay = PyPDF2.PdfReader(packet)
        pdf_writer.add_page(overlay.pages[0])

        with open(output_pdf_path, 'wb') as output_pdf_file:
            pdf_writer.write(output_pdf_file)


addLogoToPDF2("../../data/sheet/example/example.pdf","../../data/sheet/example/example2.pdf",'../../app/static/logos/logo_white.png')