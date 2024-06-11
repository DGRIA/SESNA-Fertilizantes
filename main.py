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


def show_intro():
    if st.session_state.main_page == 'Productores autorizados':
        st.markdown((
        """
            La siguiente aplicacion ha sido desarrollada para [SESNA](https://www.sesna.gob.mx/).
            El propósito de esta aplicación es la descarga, limpieza y unión de las bases de datos
            publicadas en la siguiente URL: [Programa de Fertilizantes 2023 Listados Autorizados](https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados).
        """
    ))
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        st.markdown((
        """
            La siguiente aplicacion ha sido desarrollada para [SESNA](https://www.sesna.gob.mx/).
            El propósito de esta aplicación es la descarga, limpieza y unión de las bases de datos
            publicadas en la siguiente URL: [Programa de Fertilizantes 2023 Beneficiarios Autorizados](https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados).
        """
    ))

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])  # Create three columns
    inner_cols = cols[2].columns([1, 1, 1, 1])  # Create two columns inside the middle column
    inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True) # Center the text, change the font, and add padding
    inner_cols[2].image('docs/images/mottum2.png', use_column_width=True) 


def start_process():
    cols_button = st.columns([1, 3, 1])  # Create three columns for the button
    if cols_button[1].button('Pulsa para comenzar el proceso de descarga y limpieza de datos.',
                             key='start_process_button'):
        st.session_state.button_pressed = True
        st.session_state.main_running = True
        main()

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])  # Create three columns
    inner_cols = cols[2].columns([1, 1, 1, 1])  # Create two columns inside the middle column
    inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True) # Center the text, change the font, and add padding
    inner_cols[2].image('docs/images/mottum2.png', use_column_width=True) 

def show_finished():
    if os.path.exists("data/merged_dataset.csv"):
        st.markdown("<h2 style='text-align: center;'>¡El dataset está listo!</h2>", unsafe_allow_html=True)
        cols = st.columns([1, 2, 1])
        with open("data/merged_dataset.csv", "rb") as file:
            button_clicked = cols[1].download_button(
                label="Pulsa aquí para descargar el dataset completo.",
                data=file,
                file_name="merged_dataset.csv",
                mime="text/csv",
            )
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns([1, 1, 1])  # Create three columns
        inner_cols = cols[2].columns([1, 1, 1, 1])  # Create two columns inside the middle column
        inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True) # Center the text, change the font, and add padding
        inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)  # Colocar la im

    else:
        st.markdown(
            "<h2 style='text-align: center;'>Necesitas ejecutar el proceso antes de venir a esta pantalla.</h2>",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        cols = st.columns([1, 1, 1])  # Crear tres columnas
        cols[1].image('docs/images/mottum.svg', use_column_width=True)  # Colocar la im

def advanced_analysis():
    st.markdown("<h2 style='text-align: center;'>Análisis Avanzado</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        Aquí puedes realizar análisis avanzados sobre los datos procesados.
        """
    )
    # Placeholder for advanced analysis code
    st.write("Próximamente: herramientas de análisis avanzadas.")

def secondary_page_intro():
    st.markdown("<h2 style='text-align: center;'>Introducción a la Segunda Página</h2>", unsafe_allow_html=True)
    st.write("Esta es la introducción de la segunda página. Aquí puedes añadir más detalles o instrucciones.")

def secondary_page_process():
    st.markdown("<h2 style='text-align: center;'>Proceso de la Segunda Página</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes agregar la lógica del proceso para la segunda página.")

def main():
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Directory 'data' missing, creating data directory.")
    if not os.path.exists('data/productores_autorizados'):
        os.makedirs('data/productores_autorizados')
        print("Directory 'data/productores_autorizados' missing, creating data/productores_autorizados.")

    clear_directory('data/productores_autorizados')

    with st.spinner(
            'Ejecutando scripts... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado!'):
        logger.info("Inicio de Ejecución")
        scripts = ["src/dataset_download.py", "src/data_cleaning_and_merge.py"]
        progress_bar = st.progress(0)  # Initialize progress bar
        for i, script in enumerate(scripts):
            result = subprocess.run([sys.executable, script], check=False, text=True, capture_output=True)
            progress_percent = (i + 1) / len(scripts)  # Calculate progress percentage
            progress_bar.progress(progress_percent)  # Update progress bar
            if result.returncode != 0:
                logger.error(f"{script} failed with error:\n{result.stderr}")
                break
            elif i == len(scripts) - 1:  # After the last script has run
                st.success(
                    "El proceso ha terminado. Por favor, descargue el conjunto de datos en la pestaña 'Proceso terminado'.")
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
                        st.write(
                            "No se pudo descargar ningún dataset de: https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados.\n")

                    if failed_count > 0:
                        st.write(f"Falló la descarga de {failed_count} datasets.")
                        st.selectbox("URLs de los datasets que fallaron al descargar:", failed_urls)
                    else:
                        st.write("Todos los datasets de la URL han sido descargados de forma exitosa.\n")

                    with st.spinner('Comenzando EDA...'):
                        continue

                except (IndexError, ValueError) as e:
                    st.error(f"Error parsing output from {script}: {e}")

                progress_bar.progress(1)  # Update progress bar to 100%
                logger.info("Fin de Ejecución")


if __name__ == '__main__':
    st.markdown('''
                <h1 style='text-align: center; color: black; font-size: 30px;'>Servicio de ingeniería de datos para la extracción,
                transformación y carga del Programa de Fertilizantes para el bienestar.
                </h1> 
                '''
                , unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # Sidebar
    st.sidebar.image('docs/images/SESNA-logo.png', use_column_width=True)

    st.sidebar.markdown(
        """
        La secretaria ejecutiva del Sistema Nacional Anticorrupción 
        (SESNA) es el organismo de apoyo técnico dedicado al combate 
        contra la corrupción en México.
        """
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.markdown(
        """
        Esta página ha sido desarrollada por [mottum](https://mottum.io/) con el fin de
        estandarizar, transformar y analizar los datos del Programa de Fertilizantes
        para el bienestar.
        """
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Initialize session state variables
    if 'main_page' not in st.session_state:
        st.session_state.main_page = 'Productores autorizados'
    st.session_state.main_page = st.sidebar.radio('Navegación', ['Productores autorizados', 'Beneficiarios fertilizantes 2023'])
    if st.session_state.main_page == 'Productores autorizados':
        if 'sub_page' not in st.session_state:
            st.session_state.sub_page = '1. Introducción'
        st.session_state.sub_page = st.radio('Productores autorizados', ['1. Introducción', '2. Descarga y Transformación', '3. Descarga de los datos estandarizados', '4. Análisis Avanzado'])
        if st.session_state.sub_page == '1. Introducción':
            show_intro()
        elif st.session_state.sub_page == '2. Descarga y Transformación':
            start_process()
        elif st.session_state.sub_page == '3. Descarga de los datos estandarizados':
            show_finished()
        elif st.session_state.sub_page == '4. Análisis Avanzado':
            advanced_analysis()
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        if 'second_sub_page' not in st.session_state:
            st.session_state.second_sub_page = '1. Introducción'
        st.session_state.second_sub_page = st.radio('Beneficiarios fertilizantes 2023', ['1. Introducción', '2. Proceso'])
        if st.session_state.second_sub_page == '1. Introducción':
            show_intro()
        elif st.session_state.second_sub_page == '2. Proceso':
            secondary_page_process()

    st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.markdown(
        """
        Visita los siguientes links para más información:
        """
    )

    st.sidebar.markdown(
        """
    - [Link al repositorio](https://github.com/MottumData/SESNA-Fertilizantes)
    - [Jupyter](http://localhost:8888/lab)
    """
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    st.sidebar.markdown(
        '**Financiado por:**',
        unsafe_allow_html=True
    )
    cols = st.columns([1, 1, 1]) 
    
    st.sidebar.image('docs/images/UNDP2.png', width=100)


    if 'button_pressed' not in st.session_state:
        st.session_state.button_pressed = False

    st.markdown("<br>", unsafe_allow_html=True)

# image_placeholder.image('docs/images/mottum.svg', width=500)
