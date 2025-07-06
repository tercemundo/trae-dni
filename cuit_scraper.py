import requests
from bs4 import BeautifulSoup
import time
import sys
import csv
import re

# Función para consultar un CUIT/CUIL en cuitonline.com
def consultar_cuit(numero):
    url = f"https://www.cuitonline.com/search/{numero}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Parsear el HTML con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar la meta etiqueta de descripción
            meta_description = soup.find('meta', attrs={'name': 'description'})
            
            if meta_description and 'content' in meta_description.attrs:
                content = meta_description.attrs['content']
                print(f"Contenido de meta description: {content}")
                
                # Extraer información usando expresiones regulares
                # Buscar patrones como "nombre apellido - CUIT/CUIL"
                resultados = []
                
                # Patrón para encontrar "nombre apellido - CUIT/CUIL"
                matches = re.findall(r'([\w\s]+)\s*-\s*(\d{11})', content)
                
                if matches:
                    for nombre, cuit in matches:
                        resultados.append({
                            'numero_consultado': numero,
                            'documento': cuit,
                            'nombre': nombre.strip(),
                            'actividad': "",  # No disponible en los metadatos
                            'provincia': ""    # No disponible en los metadatos
                        })
                else:
                    print(f"No se pudo extraer información del patrón para el número {numero}")
            else:
                print(f"No se encontró meta description para el número {numero}")
                
            return resultados
        else:
            print(f"Error al consultar {url}: Código de estado {response.status_code}")
            return []
    
    except Exception as e:
        print(f"Error al realizar la solicitud a {url}: {e}")
        return []

# Función principal para recorrer un rango de números
def main():
    if len(sys.argv) < 3:
        print("Uso: python cuit_scraper.py <inicio> <fin>")
        print("Ejemplo: python cuit_scraper.py 35070300 35070380")
        sys.exit(1)
    
    try:
        inicio = int(sys.argv[1])
        fin = int(sys.argv[2])
        
        if inicio > fin:
            print("El número de inicio debe ser menor o igual al número final")
            sys.exit(1)
        
        # Crear archivo CSV para guardar resultados
        with open('resultados_cuit.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['numero_consultado', 'documento', 'nombre', 'actividad', 'provincia']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            total = fin - inicio + 1
            procesados = 0
            
            print(f"Iniciando consulta de {total} números...")
            
            for numero in range(inicio, fin + 1):
                # Consultar el número actual
                resultados = consultar_cuit(numero)
                
                # Guardar resultados en CSV
                for resultado in resultados:
                    writer.writerow(resultado)
                    print(f"Guardado: {resultado['nombre']} - {resultado['documento']}")
                
                # Actualizar progreso
                procesados += 1
                porcentaje = (procesados / total) * 100
                print(f"Progreso: {procesados}/{total} ({porcentaje:.2f}%)")
                
                # Pausa para no sobrecargar el servidor
                time.sleep(1)
            
            print(f"\nConsulta finalizada. Se han procesado {procesados} números.")
            print(f"Los resultados se han guardado en 'resultados_cuit.csv'")
    
    except ValueError:
        print("Los valores de inicio y fin deben ser números enteros")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    main()