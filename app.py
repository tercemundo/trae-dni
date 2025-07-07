import streamlit as st
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import re

# Configuración de la página
st.set_page_config(page_title="Consulta de CUIT/CUIL", page_icon="📋", layout="wide")

# Título y descripción
st.title("Consulta de CUIT/CUIL por DNI")
st.markdown("Esta aplicación permite consultar información de CUIT/CUIL a partir de un rango de DNI.")

# Función para consultar un CUIT/CUIL en cuitonline.com
def consultar_cuit(numero, progress_bar, placeholder_resultados, resultados_df):
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
                st.session_state.log.append(f"Contenido de meta description para {numero}: {content}")
                
                # Extraer información usando expresiones regulares
                # Buscar patrones como "nombre apellido - CUIT/CUIL"
                resultados = []
                
                # Patrón para encontrar "nombre apellido - CUIT/CUIL"
                matches = re.findall(r'([\w\s]+)\s*-\s*(\d{11})', content)
                
                if matches:
                    for nombre, cuit in matches:
                        nuevo_resultado = {
                            'numero_consultado': numero,
                            'documento': cuit,
                            'nombre': nombre.strip(),
                            'actividad': "",  # No disponible en los metadatos
                            'provincia': ""    # No disponible en los metadatos
                        }
                        resultados.append(nuevo_resultado)
                        
                        # Agregar a DataFrame y actualizar visualización
                        resultados_df.loc[len(resultados_df)] = nuevo_resultado
                        placeholder_resultados.dataframe(resultados_df, use_container_width=True)
                else:
                    st.session_state.log.append(f"No se pudo extraer información del patrón para el número {numero}")
            else:
                st.session_state.log.append(f"No se encontró meta description para el número {numero}")
                
            return resultados
        else:
            st.session_state.log.append(f"Error al consultar {url}: Código de estado {response.status_code}")
            return []
    
    except Exception as e:
        st.session_state.log.append(f"Error al realizar la solicitud a {url}: {e}")
        return []

# Inicializar variables de sesión
if 'log' not in st.session_state:
    st.session_state.log = []

if 'resultados' not in st.session_state:
    st.session_state.resultados = pd.DataFrame(columns=['numero_consultado', 'documento', 'nombre', 'actividad', 'provincia'])

# Formulario para ingresar rango de DNI
with st.form("consulta_form"):
    col1, col2 = st.columns(2)
    with col1:
        dni_inicio = st.number_input("DNI Inicial", min_value=1000000, max_value=99999999, value=20000000)
    with col2:
        dni_fin = st.number_input("DNI Final", min_value=1000000, max_value=99999999, value=20000010)
    
    delay = st.slider("Tiempo de espera entre consultas (segundos)", min_value=1, max_value=10, value=2)
    
    submitted = st.form_submit_button("Iniciar Consulta")

# Mostrar resultados y log
col_resultados, col_log = st.columns([2, 1])

with col_resultados:
    st.subheader("Resultados")
    placeholder_resultados = st.empty()
    placeholder_resultados.dataframe(st.session_state.resultados, use_container_width=True)
    
    # Botón para descargar resultados
    if not st.session_state.resultados.empty:
        csv = st.session_state.resultados.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar resultados como CSV",
            data=csv,
            file_name="resultados_cuit.csv",
            mime="text/csv",
        )

with col_log:
    st.subheader("Log de Operaciones")
    log_container = st.container(height=400)
    with log_container:
        for log_entry in st.session_state.log:
            st.text(log_entry)

# Procesar la consulta cuando se envía el formulario
if submitted:
    # Validar el rango de DNI
    if dni_inicio > dni_fin:
        st.error("El DNI inicial debe ser menor o igual al DNI final")
    else:
        # Reiniciar resultados
        st.session_state.resultados = pd.DataFrame(columns=['numero_consultado', 'documento', 'nombre', 'actividad', 'provincia'])
        st.session_state.log = []
        
        # Mostrar mensaje de inicio
        total = dni_fin - dni_inicio + 1
        st.session_state.log.append(f"Iniciando consulta de {total} números...")
        
        # Crear barra de progreso
        progress_bar = st.progress(0)
        
        # Procesar cada número en el rango
        for i, numero in enumerate(range(dni_inicio, dni_fin + 1)):
            # Actualizar progreso
            progress = i / total
            progress_bar.progress(progress)
            
            # Consultar el número actual
            st.session_state.log.append(f"Consultando DNI: {numero}")
            resultados = consultar_cuit(numero, progress_bar, placeholder_resultados, st.session_state.resultados)
            
            # Mostrar información de progreso
            procesados = i + 1
            porcentaje = (procesados / total) * 100
            st.session_state.log.append(f"Progreso: {procesados}/{total} ({porcentaje:.2f}%)")
            
            # Pausa para no sobrecargar el servidor
            time.sleep(delay)
        
        # Completar la barra de progreso
        progress_bar.progress(1.0)
        
        # Mostrar mensaje de finalización
        st.session_state.log.append(f"\nConsulta finalizada. Se han procesado {total} números.")
        st.success(f"Consulta finalizada. Se han procesado {total} números.")