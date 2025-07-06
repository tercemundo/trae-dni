# CUIT Scraper

## Descripción
Este script de Python permite consultar información de personas a través de sus números de CUIT/CUIL en el sitio web cuitonline.com. El programa extrae los datos desde los metadatos de la página y los guarda en un archivo CSV.

## Características
- Consulta información por número de CUIT/CUIL
- Permite procesar rangos de números consecutivos
- Extrae nombre y número de documento
- Guarda los resultados en formato CSV
- Incluye manejo de errores y seguimiento de progreso

## Requisitos
Para ejecutar este script necesitas tener instalado Python 3.x y las siguientes bibliotecas:
- requests
- beautifulsoup4
- re (incluido en la biblioteca estándar)
- csv (incluido en la biblioteca estándar)
- sys (incluido en la biblioteca estándar)
- time (incluido en la biblioteca estándar)

Puedes instalar las dependencias con:
```bash
pip install -r requirements.txt