"""Frontend de facturas: consulta la API y construye un PDF en memoria."""

import os
from decimal import Decimal, InvalidOperation
from io import BytesIO
from xml.sax.saxutils import escape

import requests
from flask import Flask, abort, render_template, request, send_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

# La plantilla y los archivos estaticos se encuentran dentro de la carpeta app.
app = Flask(__name__)
# El nombre coincide con la variable declarada en Docker Compose.
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://backend:8000").rstrip("/")


def texto_seguro(valor):
    """Convierte datos recibidos en texto seguro para los parrafos de ReportLab."""
    return escape(str(valor if valor is not None else ""))


def moneda(valor):
    """Presenta numeros monetarios con dos decimales y separadores legibles."""
    try:
        return f"$ {Decimal(str(valor)):,.2f}"
    except (InvalidOperation, ValueError, TypeError):
        return "$ 0.00"


def construir_pdf(factura):
    """Devuelve un buffer PDF; no escribe archivos temporales en el servidor."""
    buffer = BytesIO()
    # Los margenes dejan espacio para cabecera, pie y tablas extensas.
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=19*mm,
                            leftMargin=19*mm, topMargin=20*mm, bottomMargin=19*mm,
                            title=f"Factura {factura.get('numero_factura', '')}")
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name="Marca", parent=estilos["Title"],
                               fontName="Helvetica-Bold", fontSize=22,
                               leading=27, textColor=colors.HexColor("#16324a")))
    estilos.add(ParagraphStyle(name="Etiqueta", parent=estilos["Normal"],
                               fontName="Helvetica-Bold", fontSize=10,
                               leading=15, textColor=colors.HexColor("#167d86")))
    estilos.add(ParagraphStyle(name="Dato", parent=estilos["Normal"],
                               fontSize=9, leading=14, wordWrap="CJK"))
    estilos.add(ParagraphStyle(name="Derecha", parent=estilos["Normal"],
                               alignment=TA_RIGHT, fontSize=9, leading=14))
    estilos.add(ParagraphStyle(name="CentroBlanco", parent=estilos["Normal"],
                               alignment=TA_CENTER, textColor=colors.white,
                               fontName="Helvetica-Bold", fontSize=8, leading=11))
    elementos = []

    # Primera seccion: nombre del documento y datos de identificacion.
    elementos.append(Paragraph("FACTURA", estilos["Marca"]))
    elementos.append(Spacer(1, 4*mm))
    elementos.append(Paragraph("Numero: " + texto_seguro(factura.get("numero_factura", "N/D")), estilos["Dato"]))
    elementos.append(Paragraph("Fecha de emision: " + texto_seguro(factura.get("fecha_emision", "N/D")), estilos["Dato"]))
    elementos.append(Spacer(1, 8*mm))

    # Segunda seccion: informacion del emisor y del destinatario.
    empresa = factura.get("empresa") or {}
    cliente = factura.get("cliente") or {}
    def datos_bloque(titulo, datos):
        lineas = [Paragraph(titulo, estilos["Etiqueta"])]
        for campo in ("nombre", "direccion", "telefono", "email"):
            if datos.get(campo):
                lineas.append(Paragraph(texto_seguro(datos[campo]).replace("\n", "<br/>"), estilos["Dato"]))
        return lineas
    columnas = Table([[datos_bloque("EMPRESA", empresa), datos_bloque("CLIENTE", cliente)]],
                     colWidths=[86*mm, 86*mm], hAlign="LEFT")
    columnas.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                  ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
    elementos.append(columnas)
    elementos.append(Spacer(1, 9*mm))

    # Tercera seccion: productos y valores de cada renglon de la factura.
    encabezado = ["Cantidad", "Descripcion", "Precio unitario", "Total"]
    tabla_datos = [[Paragraph(texto_seguro(t), estilos["CentroBlanco"]) for t in encabezado]]
    for item in factura.get("detalle", []):
        tabla_datos.append([
            Paragraph(texto_seguro(item.get("cantidad", 0)), estilos["Dato"]),
            Paragraph(texto_seguro(item.get("descripcion", "Sin descripcion")), estilos["Dato"]),
            Paragraph(moneda(item.get("precio_unitario", 0)), estilos["Derecha"]),
            Paragraph(moneda(item.get("total", 0)), estilos["Derecha"]),
        ])
    tabla = Table(tabla_datos, colWidths=[24*mm, 76*mm, 37*mm, 35*mm],
                  repeatRows=1, hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#15374c")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eff6f8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, colors.HexColor("#c7dce3")),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 8*mm))

    # Cuarta seccion: subtotal, impuesto y monto definitivo a pagar.
    totales = [
        ["Subtotal", moneda(factura.get("subtotal", 0))],
        ["Impuesto (21%)", moneda(factura.get("impuesto", 0))],
        ["TOTAL", moneda(factura.get("total", 0))],
    ]
    resumen = Table(totales, colWidths=[46*mm, 43*mm], hAlign="RIGHT")
    resumen.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d8f4f0")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#104b52")),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    elementos.append(KeepTogether([resumen, Spacer(1, 12*mm),
                                   Paragraph("Documento de demostracion generado con datos sinteticos.", estilos["Dato"])]))

    # El constructor dibuja el PDF y el cursor vuelve al principio para enviarlo.
    doc.build(elementos)
    buffer.seek(0)
    return buffer


@app.get("/")
def index():
    """Muestra el formulario principal del generador."""
    return render_template("index.html")


@app.post("/generar-pdf")
def generar_pdf():
    """Consulta la API y devuelve el PDF al navegador como descarga."""
    numero = request.form.get("id_factura", "").strip()
    if not numero or len(numero) > 80 or any(c in numero for c in "/\\\r\n"):
        return render_template("index.html", error="Ingresa un numero de factura valido."), 400
    try:
        # El tiempo limite evita que la pagina quede esperando indefinidamente.
        respuesta = requests.get(f"{BACKEND_URL}/facturas/v1/{numero}", timeout=10)
        if respuesta.status_code != 200:
            return render_template("index.html", error="No fue posible consultar esta factura."), 502
        factura = respuesta.json()
        if not isinstance(factura, dict) or not isinstance(factura.get("detalle"), list):
            return render_template("index.html", error="La API devolvio datos incompletos."), 502
        pdf = construir_pdf(factura)
        # send_file entrega un archivo PDF sin guardarlo en el disco.
        return send_file(pdf, mimetype="application/pdf", as_attachment=True,
                         download_name="factura_generada.pdf")
    except (requests.exceptions.RequestException, ValueError):
        return render_template("index.html", error="No hay conexion con el servicio de facturas."), 503
    except Exception:
        app.logger.exception("Error generando la factura")
        return render_template("index.html", error="Ocurrio un error al generar el PDF."), 500


if __name__ == "__main__":
    # Docker publica el servicio en el puerto 3000.
    app.run(host="0.0.0.0", port=3000, debug=False)
