import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from foodgram_backend.settings import PDF_FONT


def get_pdf_shoping_cart(shoping_cart):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    font_object = TTFont('Arial', PDF_FONT)
    pdfmetrics.registerFont(font_object)
    pdf.setFont('Arial', size=16)

    for i, (name, measurement_unit, amount) in enumerate(shoping_cart, 1):
        item = f'{i}. {name}: {amount}{measurement_unit}'
        pdf.drawString(50, 775 - i * 25, item)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
