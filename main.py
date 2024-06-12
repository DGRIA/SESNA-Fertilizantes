import streamlit as st
import subprocess
import logging
import config
import sys
import os
import shutil
import pandas as pd
import base64
from io import StringIO
from src.dataset_download import download_datasets
from src.data_cleaning_and_merge import data_cleaning, data_cleaning2
from src.scrape_urls import scrape_urls
from streamlit_option_menu import option_menu as om
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

def data_cleaning_function(dataset):
    if dataset == 'productores_autorizados_2023':
        data_cleaning()
        st.success("El proceso de limpieza de datos ha terminado. En la siguiente pestaña puede proceder con la descarga de los datos estandarizados.")
    elif dataset == 'beneficiarios_fertilizantes_2023':
        data_cleaning2()
        st.success("El proceso de limpieza de datos ha terminado. En la siguiente pestaña puede proceder con la descarga de los datos estandarizados.")

def show_intro():
    if st.session_state.main_page == 'Productores autorizados 2023':
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
            publicadas en la siguiente URL: [Programa de Fertilizantes 2023 Beneficiarios Autorizados](https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-de-beneficiarios).
        """
    ))
        
    st.markdown("<br>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Suba el diccionario manual para empezar el proceso.")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("cp1252"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Check if the file is a CSV (or similar) before trying to read it as a DataFrame
        if uploaded_file.name.endswith('.csv'):
            # Reset the StringIO object to the beginning
            stringio.seek(0)
            dataframe = pd.read_csv(stringio)
            dataframe.to_csv(os.path.join('data', uploaded_file.name))
        else:
            st.write("Uploaded file is not a CSV file.")

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])  # Create three columns
    inner_cols = cols[2].columns([1, 1, 1, 1])  # Create two columns inside the middle column
    inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True) # Center the text, change the font, and add padding
    inner_cols[2].image('docs/images/mottum2.png', use_column_width=True) 

def start_process():
    if st.session_state.main_page == 'Productores autorizados 2023':
        cols_button = st.columns([1, 3, 1])
        if cols_button[1].button('Descargar Listado Autorizados2023.', key='start_process_button'):
            data_download("https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados",  "data/productores_autorizados")
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns([1, 1, 1])
        inner_cols = cols[2].columns([1, 1, 1, 1])
        inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True)
        inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        cols_button = st.columns([1, 3, 1])
        if cols_button[1].button('Descargar Listado Beneficiarios2023.', key='start_process_button'):
            data_download("https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-de-beneficiarios",  "data/productores_beneficiarios")
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns([1, 1, 1])
        inner_cols = cols[2].columns([1, 1, 1, 1])
        inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True)
        inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)

def data_download(url, download_destination_folder):
    if not os.path.exists('data'):
            os.makedirs('data')
            print("Directory 'data' missing, creating data directory.")
    if not os.path.exists('data/productores_autorizados'):
        os.makedirs('data/productores_autorizados')
        print("Directory 'data/productores_autorizados' missing, creating data/productores_autorizados.")
    if not os.path.exists('data/productores_beneficiarios'):
        os.makedirs('data/productores_autorizados')
        print("Directory 'data/productores_autorizados' missing, creating data/productores_autorizados.")

    clear_directory('data/productores_autorizados')
    clear_directory('data/productores_beneficiarios')
    with st.spinner(
            'Ejecutando scripts... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado!'
        ):
        progress_bar = st.progress(0)
        download_urls = []
        urls = scrape_urls(url)
        progress_bar.progress(0.33)
        for url in urls:
            download_urls.append(url)
        result = download_datasets(download_urls, download_destination_folder)
        progress_bar.progress(0.66)

        good_count = result['good_count']
        good_urls = result['good_urls']
        failed_count = result['failed_count']
        failed_urls = result['failed_urls']

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

        all_urls = good_urls + failed_urls
        statuses = ['TRUE' if url in good_urls else 'FALSE' for url in all_urls]
        dataset = pd.DataFrame({
            'id': range(1, len(all_urls) + 1),
            'url': all_urls,
            'estado_de_descarga': statuses
        })

        # Convert the DataFrame to a CSV file
        csv = dataset.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="dataset.csv">Download CSV File</a>'

        # Create a download button for the CSV file
        st.markdown(href, unsafe_allow_html=True)

        progress_bar.progress(1)  # Update progress bar to 100%
        logger.info("Fin de Ejecución")
        st.success(
            "El proceso de descarga ha terminado. En la siguiente pestaña puede proceder con la limpieza de los datos."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])  # Create three columns
    inner_cols = cols[2].columns([1, 1, 1, 1])  # Create two columns inside the middle column
    inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True) # Center the text, change the font, and add padding
    inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)

def clean_data_screen():
    if st.session_state.main_page == 'Productores autorizados 2023':
        with st.spinner(
            'Ejecutando scripts... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado!'
        ):
            cols_button = st.columns([1, 3, 1])
            if cols_button[1].button('Limpieza de datos de Listado Productores2023.', key='start_process_button'):
                data_cleaning_function('productores_autorizados_2023')
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns([1, 1, 1])
            inner_cols = cols[2].columns([1, 1, 1, 1])
            inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True)
            inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        with st.spinner(
            'Ejecutando scripts... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado!'
        ):
            cols_button = st.columns([1, 3, 1])
            if cols_button[1].button('Limpieza de datos de Listado Beneficiarios2023.', key='start_process_button'):
                data_cleaning_function('beneficiarios_fertilizantes_2023')
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns([1, 1, 1])
            inner_cols = cols[2].columns([1, 1, 1, 1])
            inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True)
            inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)

def show_finished():
    if st.session_state.main_page == 'Productores autorizados 2023':
        if os.path.exists("data/listado_productores_complete2023.csv"):
            st.markdown("<h2 style='text-align: center;'>¡El dataset está listo!</h2>", unsafe_allow_html=True)
            cols = st.columns([1, 2, 1])
            with open("data/listado_productores_complete2023.csv", "rb") as file:
                button_clicked = cols[1].download_button(
                    label="Pulsa aquí para descargar el dataset completo.",
                    data=file,
                    file_name="listado_productores_completo2023.csv",
                    mime="text/csv",
                )
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns([1, 1, 1])  # Create three columns
            inner_cols = cols[2].columns([1, 1, 1, 1])  # Create two columns inside the middle column
            inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True) # Center the text, change the font, and add padding
            inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        if os.path.exists("data/LISTADO_BENEFICIARIOS2023_COMPLETO.csv"):
            st.markdown("<h2 style='text-align: center;'>¡El dataset está listo!</h2>", unsafe_allow_html=True)
            cols = st.columns([1, 2, 1])
            with open("data/LISTADO_BENEFICIARIOS2023_COMPLETO.csv", "rb") as file:
                button_clicked = cols[1].download_button(
                    label="Pulsa aquí para descargar el dataset completo.",
                    data=file,
                    file_name="LISTADO_BENEFICIARIOS2023_COMPLETO.csv",
                    mime="text/csv",
                )
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns([1, 1, 1])  # Create three columns
            inner_cols = cols[2].columns([1, 1, 1, 1])  # Create two columns inside the middle column
            inner_cols[0].markdown("<p style='text-align: center; font-family: Comic Sans MS; padding-top: 12px; white-space: nowrap;'>Made with love</p>", unsafe_allow_html=True) # Center the text, change the font, and add padding
            inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)

    else:
        st.markdown(
            "<h2 style='text-align: center;'>Necesitas ejecutar el proceso antes de venir a esta pantalla.</h2>",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        cols = st.columns([1, 1, 1])  # Crear tres columnas
        cols[1].image('docs/images/mottum.svg', use_column_width=True)  # Colocar la im


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

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if 'main_page' not in st.session_state:
        st.session_state.main_page = 'Productores autorizados 2023'
    with st.sidebar:
        st.session_state.main_page = om('Main menu', ['Productores autorizados 2023', 'Beneficiarios fertilizantes 2023'], icons=["list-task", "list-task"], menu_icon="cast")
    if st.session_state.main_page == 'Productores autorizados 2023':
        if 'sub_page' not in st.session_state:
            st.session_state.sub_page = '1. Introducción'
        st.session_state.sub_page = st.radio('Productores autorizados 2023', ['1. Introducción', '2. Descarga y Transformación', '3. Limpieza de datos', '4. Descarga de los datos estandarizados'])
        if st.session_state.sub_page == '1. Introducción':
            show_intro()
        elif st.session_state.sub_page == '2. Descarga y Transformación':
            start_process()
        elif st.session_state.sub_page == '3. Limpieza de datos':
            clean_data_screen()
        elif st.session_state.sub_page == '4. Descarga de los datos estandarizados':
            show_finished()
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        if 'second_sub_page' not in st.session_state:
            st.session_state.second_sub_page = '1. Introducción'
        st.session_state.second_sub_page = st.radio('Beneficiarios fertilizantes 2023', ['1. Introducción', '2. Descarga y Transformación', '3. Limpieza de datos', '4. Descarga de los datos estandarizados'])
        if st.session_state.second_sub_page == '1. Introducción':
            show_intro()
        elif st.session_state.second_sub_page == '2. Descarga y Transformación':
            start_process()
        elif st.session_state.second_sub_page == '3. Limpieza de datos':
            clean_data_screen()
        elif st.session_state.second_sub_page == '4. Descarga de los datos estandarizados':
            show_finished()

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
    # Initialize session state variables
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
