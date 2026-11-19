# Validacion del Taller 2

- Se revisaron todos los archivos entregados en el ZIP original.
- El backend fue verificado con pytest: **3 pruebas aprobadas**.
- Las **6 verificaciones del frontend** estan incluidas en `tests/test_frontend.py`, pero no pudieron ejecutarse aqui porque Flask no esta instalado en el entorno disponible.
- Se comprobo la compilacion sintactica de los modulos Python.
- Se creo y renderizo correctamente un PDF de muestra usando ReportLab, sin iniciar Flask.
- Se verifico la presencia de las referencias a Bootstrap, CSS y JavaScript.
- Docker no esta disponible en este entorno; el conjunto completo debe probarse en Docker Desktop.
- La hoja de Bootstrap se carga desde CDN y requiere conectividad de internet.

## Comprobacion en el computador del estudiante

1. `docker compose up --build`
2. Abrir `http://localhost:3000` y generar `FAC-2026-001`.
3. Comprobar el archivo PDF descargado.
4. Comprobar `http://localhost:8000/` y `http://localhost:8000/docs`.
5. Instalar las dependencias de ambos servicios mas `pytest` y ejecutar `python -m pytest -v tests`.

El PDF de `ejemplos/factura_ejemplo.pdf` demuestra el formato; sus datos no son reales.
