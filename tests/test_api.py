"""Pruebas basicas del servicio FastAPI, sin conectar con servicios externos."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("taller2_backend", ROOT / "backend/app/main.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


def test_salud():
    # Confirma que el healthcheck usado por Docker responde correctamente.
    assert backend.health()["status"] == "ok"


def test_factura_contiene_datos_y_totales():
    # Comprueba campos importantes del documento solicitado por el docente.
    factura = backend.get_factura("FAC-2026-001")
    assert factura["numero_factura"] == "FAC-2026-001"
    assert factura["empresa"]["nombre"]
    assert factura["cliente"]["nombre"]
    assert 1 <= len(factura["detalle"]) <= 5
    assert factura["subtotal"] >= 0
    assert factura["impuesto"] == round(factura["subtotal"] * .21, 2)
    assert factura["total"] == round(factura["subtotal"] + factura["impuesto"], 2)


def test_detalle_calcula_importes():
    # Cada producto incluye cantidad y precio unitario positivos.
    factura = backend.get_factura("DEMO-002")
    for item in factura["detalle"]:
        assert 1 <= item["cantidad"] <= 10
        assert item["precio_unitario"] > 0
        assert abs(item["total"] - round(item["cantidad"] * item["precio_unitario"], 2)) < 0.01
