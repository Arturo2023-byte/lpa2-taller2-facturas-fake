# LPA2 - Taller 2 | Generador de facturas PDF

Proyecto academico de dos servicios: **FastAPI + Faker** para datos sinteticos y **Flask + ReportLab** para presentar el formulario y descargar un PDF. Interfaz oscura con **Bootstrap 5 y CSS personalizado**.

## Autor

- Nombre: [Completar por el estudiante]
- GitHub: [Completar]

## Requisitos del taller

- Backend FastAPI en el puerto **8000** con endpoint `GET /facturas/v1/{numero_factura}`.
- Datos sinteticos de empresa, cliente, detalle, subtotal, impuesto (21%) y total.
- Frontend Flask en el puerto **3000** con formulario de numero de factura.
- Consulta HTTP del frontend al backend y generacion del PDF usando ReportLab.
- Descarga del archivo PDF, configuracion Docker Compose y documentacion de uso.

## Estructura

```text
lpa2-taller2-main/
├── backend/
│   ├── Dockerfile
│   └── app/
│       ├── main.py                 # API y datos sinteticos
│       └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   └── app/
│       ├── main.py                 # Consulta API y crea PDF
│       ├── requirements.txt
│       ├── templates/index.html    # Bootstrap, formulario y tarjetas
│       └── static/
│           ├── css/style.css      # Tema oscuro personalizado
│           └── js/app.js          # Mensaje al enviar formulario
├── tests/                          # Verificaciones automatizadas
├── docker-compose.yml
└── README.md
```

## Iniciar con Docker

1. Instalar Docker Desktop y activar Docker Compose.
2. Abrir la carpeta principal en VS Code y ejecutar:

```bash
docker compose up --build
```

3. Abrir los servicios:

| Servicio | Direccion |
|---|---|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| API Swagger | http://localhost:8000/docs |
| API ReDoc | http://localhost:8000/redoc |

4. En el formulario ingresar, por ejemplo, `FAC-2026-001`, y seleccionar **Generar y descargar PDF**.
5. Se obtiene `factura_generada.pdf` con informacion ficticia.

Detener los contenedores con `docker compose down`.

## Comprobar la API

```bash
curl http://localhost:8000/
curl http://localhost:8000/facturas/v1/FAC-2026-001
```

El numero de factura es un identificador libre. Cada consulta puede producir informacion distinta porque Faker genera datos nuevos.

## Ejecutar sin Docker

Crear y activar dos entornos virtuales (uno por servicio). Instalar las dependencias de los archivos `requirements.txt`. Ejecutar desde `backend/app`:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Para el frontend establecer `BACKEND_API_URL=http://localhost:8000` y ejecutar desde `frontend/app`:

```bash
python main.py
```

## Pruebas

Las pruebas automatizadas incluidas verifican la estructura de los datos de la API y el generador PDF, usando clientes simulados sin requerir una API real. Requieren `pytest` y las dependencias de ambos servicios.

```bash
python -m pytest -v tests
```

## Detalles del estilo

- `index.html` incluye grilla, formulario y tarjetas con clases Bootstrap 5.
- `style.css` sobrescribe el aspecto visual con una identidad azul oscuro y turquesa.
- `app.js` muestra el estado de envio sin alterar la descarga.
- Bootstrap se carga desde CDN: **con conexion a internet** se visualizan sus componentes; el CSS personalizado permanece disponible localmente.
- El CSS no altera los impuestos ni los datos. El PDF tiene su propio estilo con ReportLab.

## Errores comunes

- **La pagina no abre:** comprobar `docker compose ps` y los puertos 3000 y 8000.
- **La API no responde:** consultar `docker compose logs backend`.
- **No descarga:** verificar `docker compose logs frontend`, el numero de factura y que el backend funcione.
- **No aparece Bootstrap:** comprobar conectividad a internet; la plantilla usa el CDN de Bootstrap.

Los datos son **sinteticos** y no representan facturas tributarias reales. Este proyecto es demostrativo y no emite documentos fiscales validos.
