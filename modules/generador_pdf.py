from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
from datetime import datetime

def crear_pdf_dispensa(nombre, dni, motivo, distrito):
    # 1. Crear un buffer de memoria (un archivo virtual)
    buffer = io.BytesIO()
    
    # 2. Configurar el "lienzo" (Canvas)
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- CABECERA ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 1 * inch, "SOLICITA: DISPENSA/JUSTIFICACIÓN DE MULTA ELECTORAL")
    
    c.setFont("Helvetica", 10)
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    c.drawRightString(width - 1 * inch, height - 1.5 * inch, f"Lima, {fecha_hoy}")
    
    # --- DESTINATARIO ---
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1 * inch, height - 2.5 * inch, "SEÑORES DEL JURADO NACIONAL DE ELECCIONES")
    
    # --- CUERPO ---
    c.setFont("Helvetica", 11)
    texto_inicio = height - 3.5 * inch
    linea = 15 # Espacio entre lineas
    
    c.drawString(1 * inch, texto_inicio, f"Yo, {nombre.upper()}, identificado con DNI N° {dni},")
    c.drawString(1 * inch, texto_inicio - linea, f"con domicilio en el distrito de {distrito}, ante ustedes me presento y expongo:")
    
    c.drawString(1 * inch, texto_inicio - (linea*3), "Que, por medio del presente documento, solicito la dispensa/justificación")
    c.drawString(1 * inch, texto_inicio - (linea*4), "de la multa electoral correspondiente a las últimas elecciones, debido a:")
    
    # Motivo (Aquí va lo que escribe el usuario)
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(1.5 * inch, texto_inicio - (linea*6), f'"{motivo}"')
    
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, texto_inicio - (linea*8), "Adjunto a la presente los documentos probatorios correspondientes.")
    
    # --- PIE DE PAGINA ---
    c.drawString(1 * inch, texto_inicio - (linea*12), "Por lo expuesto, ruego a ustedes acceder a mi solicitud.")
    
    # Linea de firma
    c.line(2.5 * inch, 3 * inch, 5.8 * inch, 3 * inch)
    c.drawCentredString(width / 2, 2.8 * inch, f"{nombre.upper()}")
    c.drawCentredString(width / 2, 2.65 * inch, f"DNI: {dni}")

    # 3. Guardar el PDF
    c.showPage()
    c.save()
    
    # 4. Rebobinar el buffer para que se pueda leer desde el principio
    buffer.seek(0)
    return buffer