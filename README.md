# Clasificar Facturas

Sistema de clasificación automática de facturas (Windows-friendly) para:
- Agrupar facturas iguales por tipo (Tipo_1, Tipo_2, ...)
- Vincular tipo ↔ proveedor desde Excel (fuente) → JSON (cache)
- Extraer fecha, proveedor y número de factura por patrones
- Renombrar a YYYYMMDD_Proveedor_NumFactura.pdf
- Enrutar a carpeta de estación o a Pendientes_de_identificar

## Estructura del proyecto

```
facturas-classifier/
├─ data/
│  ├─ samples/                # PDFs/imagenes de entrada
│  ├─ out/
│  │  ├─ tipos/               # Tipo_1, Tipo_2, ...
│  │  ├─ renombradas/         # Archivos ya renombrados
│  │  ├─ estaciones/          # Carpeta final por estación
│  │  └─ Pendientes_de_identificar/
│  ├─ Proveedores/            # Excel original (hoja Proveedores)
│  └─ providers.json          # Cache normalizada generada desde Excel
├─ patterns/
│  └─ patterns.yaml           # Patrones por Tipo_x: fecha, nombre, num
├─ src/
│  ├─ cluster.py              # Detección de “facturas iguales” (pHash/visual)
│  ├─ text_extract.py         # Texto (PyPDF) + OCR (Tesseract) fallback
│  ├─ link_providers.py       # Vincula tipo con proveedor (usa providers.json)
│  ├─ fields_extract.py       # Extrae fecha/proveedor/num con regex por tipo
│  ├─ rename_and_route.py     # Renombra y enruta
│  ├─ providers_sync.py       # Sincroniza Excel→JSON
│  └─ main.py                 # CLI por etapas
├─ requirements.txt
└─ .env.example               # Rutas/idioma OCR, etc.
```

## Requisitos (Windows)

1) Instala Tesseract OCR para Windows (UB Mannheim recomendado) y apunta su ruta, por ejemplo:
`C:\\Program Files\\Tesseract-OCR\\tesseract.exe`

2) Crea y activa entorno virtual (opcional pero recomendado):
```powershell
python -m venv venv
venv\Scripts\activate
```

3) Instala dependencias:
```powershell
pip install -r requirements.txt
```

4) Configura `.env` según `.env.example` si necesitas ruta específica de Tesseract.

## Excel de proveedores (fuente) → JSON (cache)
- Excel fuente: `data/Proveedores/Proveedores.xlsx`, hoja: `Proveedores`
- Columnas: `Proveedor | CIF | EstacionDestino`
- Generar/actualizar JSON:
```powershell
python -m src.main providers
```

## Patrones por tipo (`patterns/patterns.yaml`)
Ejemplo inicial:
```
Tipo_1:
  proveedor_regex: "(ACME\\s+GASOLINERA\\s+S\\.?A\\.?)"
  fecha_regex: "(\\d{2}/\\d{2}/\\d{4})"
  fecha_out_format: "%d/%m/%Y"
  numero_regex: "Factura\\s*(?:nº|num\\.?|No\\.?):?\\s*([A-Z0-9-]+)"
Tipo_2:
  proveedor_regex: "(HIDROCARBUROS\\s+DEL\\s+SUR)"
  fecha_regex: "(\\d{4}-\\d{2}-\\d{2})"
  fecha_out_format: "%Y-%m-%d"
  numero_regex: "N.?\\s*Factura\\s*[:#]?\\s*([A-Z0-9/.-]+)"
```

## Uso (CLI por etapas)

Desde la raíz del proyecto:

```powershell
# 0) Sincronizar proveedores (Excel → JSON)
python -m src.main providers

# 1) Agrupar por tipo usando pHash
python -m src.main cluster --max-hamming 5

# 2) Vincular tipos con proveedores (usa providers.json; revisa 'data/out/tipo_proveedor_map.csv')
python -m src.main link

# 3) Extraer campos y renombrar preliminarmente
python -m src.main extract

# 4) Enrutar a estaciones o a Pendientes_de_identificar
python -m src.main route
```

## Consejos de mejora
- Si hay falsos positivos en clustering: añade n_páginas, tamaño, doble hash (pHash+aHash), o subtipos.
- Mejora del vínculo proveedor: busca CIF/dominio/dirección, normaliza texto, sinónimos.
- Control de calidad: genera CSV con origen, Tipo_x, proveedor, fecha/número, destino; si >20% pendientes, ajusta patrones.

## Nota
No subas facturas reales al repositorio público.
