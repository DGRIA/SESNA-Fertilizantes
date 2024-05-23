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
    st.image('docs/images/mottum2.svg', width=660)
    clear_directory('data/fertilizantes_autorizados')
    with st.spinner('Ejecutando scripts... Por favor espera.'):
        logger.info("Inicio de Ejecución")
        scripts = ["src/dataset_download.py", "src/eda.py", "src/merge.py"]
        for i, script in enumerate(scripts):
            result = subprocess.run([sys.executable, script], check=False, text=True, capture_output=True)
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
                        st.write(f"{good_count} datasets se han descargado de forma exitosa. URLs: {good_urls}")
                    else:
                        st.write("No se pudo descargar ningún dataset de: https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados.\n")
                    
                    if failed_count > 0:
                        st.write(f"Falló la descarga de {failed_count} datasets. URLs: {failed_urls}")
                    else:
                        st.write("Todos los datasets de la URL han sido descargados de forma exitosa.\n")
                    
                    st.write("Comenzando EDA.\n")
                except (IndexError, ValueError) as e:
                    st.error(f"Error parsing output from {script}: {e}")

            elif i == 1:  # After the first script has run
                st.write("\nEDA terminado.\n")
                st.write("Comenzando merge.\n")
            elif i == 2:  # After the first script has run
                st.write("El dataset esta listo!")
                with open("data/productores_autorizados_final.csv", "rb") as file:
                            st.download_button(
                                label="Descargar dataset",
                                data=file,
                                file_name="productores_autorizados_final.csv",
                                mime="text/csv",
                            )
                logger.info("Fin de Ejecución")

if __name__ == '__main__':
    col1, col2, col3 = st.columns(3)
    col1.write("\n" * 10)

    col1.image('docs/images/mottumfav.svg', width=200)
    col2.markdown("<h1 style='text-align: center; color: white;'> & </h1>", unsafe_allow_html=True)
    col3.image('docs/images/SESNA.png', width=300)
    st.title('Fertilizantes Dataset')
    if st.button('Descarga directa fertilizantes autorizados'):
        main()
    st.image('docs/images/mottum2.svg', width=660)