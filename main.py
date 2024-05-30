import streamlit as st
import subprocess
import logging
import config
import sys
import os
import shutil

# Incluir estas líneas en cada script para registrar los logs
logger = logging.getLogger("Fertilizantes")
logger.setLevel(logging.INFO)

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def main():
    clear_directory('data/productores_autorizados')
    with st.spinner('Ejecutando scripts... Esto puede tardar unos minutos.'):
        logger.info("Inicio de Ejecución")
        scripts = ["src/dataset_download.py", "src/eda.py", "src/merge.py"]
        progress_bar = st.progress(0)  # Initialize progress bar
        for i, script in enumerate(scripts):
            result = subprocess.run([sys.executable, script], check=False, text=True, capture_output=True)
            progress_percent = (i + 1) / len(scripts)  # Calculate progress percentage
            progress_bar.progress(progress_percent)  # Update progress bar
            if result.returncode != 0:
                logger.error(f"{script} failed with error:\n{result.stderr}")
                break
            elif i == 0:  # After the first script has run
                lines = [line for line in result.stdout.split('\n') if line]  # Ignore empty lines
                try:
                    # Extract the section with the download results
                    start_index = lines.index("====DOWNLOAD RESULTS====") + 1
                    failed_count = int(lines[start_index])
                    failed_urls = lines[start_index + 1].split(',')
                    good_count = int(lines[start_index + 2])
                    good_urls = lines[start_index + 3].split(',')

                    if good_count > 0:
                        st.write(f"{good_count} datasets se han descargado de forma exitosa.")
                        st.selectbox("URLs de los datasets descargados con éxito:", good_urls)
                    else:
                        st.write("No se pudo descargar ningún dataset de: https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados.\n")

                    if failed_count > 0:
                        st.write(f"Falló la descarga de {failed_count} datasets.")
                        st.selectbox("URLs de los datasets que fallaron al descargar:", failed_urls)
                    else:
                        st.write("Todos los datasets de la URL han sido descargados de forma exitosa.\n")

                    with st.spinner('Comenzando EDA...'):
                        continue
                except (IndexError, ValueError) as e:
                        st.error(f"Error parsing output from {script}: {e}")
                    

            elif i == 1:  # After the first script has run
                st.write("\nEDA terminado.\n")
                st.write("Comenzando merge...\n")
            elif i == 2:  # After the first script has run
                st.write("¡El dataset está listo!")
                with open("data/productores_autorizados_final.csv", "rb") as file:
                            st.download_button(
                                label="Pulsa aquí para descargar el dataset completo.",
                                data=file,
                                file_name="productores_autorizados_final.csv",
                                mime="text/csv",
                            )
                logger.info("Fin de Ejecución")

if __name__ == '__main__':
    st.markdown("<h1 style='text-align: center; color: black;'>Datos de Fertilizantes Autorizados</h1>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns([1,5,1])  # Create three columns
    cols[1].image('docs/images/SESNA2.png', width=500) 

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander(("Productores autorizados")):
        st.markdown((
            """
        La Siguiente solución ha sido desarrollada para el laboratorio de UNPD de SESNA. 
        """
        ))
    st.markdown("<br>", unsafe_allow_html=True)
    # Sidebar
    st.sidebar.header("Sobre la aplicación")
    st.sidebar.markdown(
        """
        La siguiente aplicacion ha sido desarrollada para [SESNA](https://www.sesna.gob.mx/).
        El propósito de esta aplicación es la descarga, limpieza y unión de las bases de datos
        publicadas en la siguiente URL: [Programa de Fertilizantes 2023 Listados Autorizados](https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados).
        """
    )

    st.sidebar.header("Documentación y herramientas")
    st.sidebar.markdown(
        """
    - [Documentación de Streamlit](https://docs.streamlit.io/)
    - [Cheat sheet](https://docs.streamlit.io/library/cheatsheet)
    - [Book](https://www.amazon.com/dp/180056550X) (Getting Started with Streamlit for Data Science)
    - [Blog](https://blog.streamlit.io/how-to-master-streamlit-for-data-science/) (How to master Streamlit for data science)
    """
    )

    st.sidebar.header("Sobre Mottum")
    st.sidebar.markdown(
        "En [mottum](https://mottum.io/) nos compromentemos con un useo responsable de las ciencia de datos y la inteligencia artificial (IA) para resolver desafíos complejos de gobiernos y organizaciones."
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.image('docs/images/mottum.svg', width= 400)

    cols_button = st.columns([1,3,1])  # Create three columns for the button
    if cols_button[1].button('Pulsa para comenzar el proceso de descarga y limpieza de datos.'):
        main()
