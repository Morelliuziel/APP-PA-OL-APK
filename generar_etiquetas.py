#!/usr/bin/env python3
"""Regenera muestras QR imprimibles, a partir de inventario_ejemplo.json."""
import json, pathlib, qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parent
TAR = ROOT / 'etiquetas'
TAR.mkdir(exist_ok=True)
TABLETS = json.loads((TAR / 'inventario_ejemplo.json').read_text(encoding='utf-8'))
for t in TABLETS:
    raw = json.dumps(t, ensure_ascii=False, separators=(',', ':'))
    (TAR/f"{t['serial']}.txt").write_text(raw + '\n', encoding='utf-8')
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
    q.add_data(raw); q.make(fit=True)
    img = q.make_image(fill_color='black', back_color='white').convert('RGB')
    img.save(TAR/f"{t['serial']}.png")

pdfpath = TAR/'Etiquetas_QR_Imprimir_A4.pdf'
c = canvas.Canvas(str(pdfpath), pagesize=A4)
w,h = A4
c.setTitle('Pañol-App - Etiquetas QR de prueba')
c.setFont('Helvetica-Bold', 18)
c.setFillColor(HexColor('#102039'))
c.drawString(40,h-47,'PAÑOL-APP | Etiquetas de prueba')
c.setFont('Helvetica', 9)
c.setFillColor(HexColor('#64748b'))
c.drawString(40,h-64,'Imprimir al 100% (sin ajustar). Datos ficticios para demostración escolar.')
for i,t in enumerate(TABLETS):
    ytop = h-94-i*234
    c.setStrokeColor(HexColor('#CFD8E3'))
    c.roundRect(35,ytop-222,w-70,214,10,stroke=1,fill=0)
    imgpath = TAR/f"{t['serial']}.png"
    c.drawImage(str(imgpath),51,ytop-201,width=186,height=186,mask='auto')
    x = 249
    c.setFillColor(HexColor('#102039')); c.setFont('Helvetica-Bold',14)
    c.drawString(x,ytop-32,t['serial'])
    c.setFont('Helvetica',10)
    lines = [f"Procesador: {t['procesador']}", f"RAM: {t['ram_gb']} GB", f"Almacenamiento: {t['almacenamiento_gb']} GB", f"Pantalla: {t['pantalla_pulgadas']} pulgadas", f"Puertos: {', '.join(t['puertos'])}", f"Redes: {', '.join(t['conectividad'])}"]
    for j,line in enumerate(lines):
        c.drawString(x,ytop-62-20*j,line)
    c.setFont('Helvetica-Oblique',9)
    c.setFillColor(HexColor('#64748b'))
    c.drawString(x,ytop-195,'QR con ficha técnica (JSON v1)')
c.save()
print(pdfpath)
