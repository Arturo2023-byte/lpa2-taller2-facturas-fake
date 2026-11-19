"""Verificaciones del formulario y la generacion PDF con cliente simulado."""
import importlib.util
from pathlib import Path
from unittest.mock import patch
import pytest

pytest.importorskip("flask")
pytest.importorskip("reportlab")
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("taller2_frontend", ROOT / "frontend/app/main.py")
frontend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontend)


def ejemplo():
    # Datos artificiales para evitar depender de internet durante las pruebas.
    return {
        "numero_factura":"FAC-001", "fecha_emision":"2026-11-06",
        "empresa":{"nombre":"Empresa Ejemplo", "direccion":"Calle 1", "telefono":"123", "email":"demo@example.org"},
        "cliente":{"nombre":"Cliente Ejemplo", "direccion":"Calle 2", "telefono":"456"},
        "detalle":[{"cantidad":2, "descripcion":"Servicio de prueba", "precio_unitario":100, "total":200}],
        "subtotal":200, "impuesto":42, "total":242
    }


def test_pdf_es_valido():
    # Un archivo PDF debe iniciar con la cabecera %PDF.
    datos = frontend.construir_pdf(ejemplo()).getvalue()
    assert datos.startswith(b"%PDF-")
    assert len(datos) > 1000


def test_pagina_principal():
    # Flask debe mostrar el formulario inicial.
    cliente = frontend.app.test_client()
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert b'id_factura' in respuesta.data


def test_descarga_pdf_con_api_simulada():
    # La API se sustituye para comprobar solo el flujo del frontend.
    from unittest.mock import Mock
    respuesta_api = Mock(status_code=200)
    respuesta_api.json.return_value = ejemplo()
    with patch.object(frontend.requests, "get", return_value=respuesta_api):
        respuesta = frontend.app.test_client().post("/generar-pdf", data={"id_factura":"FAC-001"})
    assert respuesta.status_code == 200
    assert respuesta.mimetype == "application/pdf"
    assert respuesta.data.startswith(b"%PDF-")


def test_numero_vacio_se_rechaza():
    # Un identificador vacio no debe consultarse al backend.
    respuesta = frontend.app.test_client().post("/generar-pdf", data={"id_factura":" "})
    assert respuesta.status_code == 400


def test_api_no_disponible():
    # La desconexion de la API se presenta como error controlado.
    import requests
    with patch.object(frontend.requests, "get", side_effect=requests.exceptions.ConnectionError):
        respuesta = frontend.app.test_client().post("/generar-pdf", data={"id_factura":"FAC-001"})
    assert respuesta.status_code == 503
