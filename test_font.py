from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('LibSans', '/usr/share/fonts/liberation/LiberationSans-Regular.ttf'))

c = canvas.Canvas("test_font.pdf")
c.setFont("LibSans", 20)
c.drawString(100, 100, "Naira: ₦500")
c.save()
print("Done")
