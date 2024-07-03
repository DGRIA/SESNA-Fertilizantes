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
from src.data_cleaning_and_merge import data_cleaning, data_cleaning2, load_datasets
from src.scrape_urls import scrape_urls, scrape_xlsx
from streamlit_option_menu import option_menu as om
import requests

# Incluir estas líneas en cada script para registrar los logs
logger = logging.getLogger("Fertilizantes")
logger.setLevel(logging.INFO)


def session_state_with_love_mottum(unique_id):
    # Construct a unique session state key based on the provided unique_id
    key = f'love_mottum_displayed_{unique_id}'

    # Check if this unique key is in the session state and initialize it if not
    if key not in st.session_state:
        st.session_state[key] = False

    # Always check the session state and display the motto if it has been shown before
    # This ensures the motto remains visible across all page navigations
    if st.session_state[key]:
        display_love_mottum()
    else:
        # The first time the motto is to be displayed, set the session state to True
        display_love_mottum()
        st.session_state[key] = True


def convert_xlsx_to_csv_in_directory(directory_path):
    # List all .xlsx files in the directory
    xlsx_files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
    total_files = len(xlsx_files)

    if total_files == 0:
        st.write("No .xlsx files found to convert.")
        return

    # Initialize the progress bar
    progress_bar = st.progress(0)

    for index, filename in enumerate(xlsx_files, start=1):
        # Construct full file path
        file_path = os.path.join(directory_path, filename)
        # Read the .xlsx file
        df = pd.read_excel(file_path)
        # Construct the .csv filename
        csv_filename = filename.replace('.xlsx', '.csv')
        csv_file_path = os.path.join(directory_path, csv_filename)
        # Save as .csv
        df.to_csv(csv_file_path, index=False)
        print(f"Converted {filename} to {csv_filename}")

        # Update the progress bar
        progress_bar.progress(index / total_files)

    st.write("All files have been converted.")


def display_love_mottum():
    """Displays the 'Made with love' motto and logo."""
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])  # Create three columns
    inner_cols = cols[2].columns([1, 1, 1, 1])  # Create four columns inside the third main column
    inner_cols[0].markdown(
        "<p style='text-align: center; font-family: Manrope; padding-top: 12px; white-space: nowrap;'>Made with love</p>",
        unsafe_allow_html=True)  # Center the text, change the font, and add padding
    inner_cols[2].image('docs/images/mottum2.png', use_column_width=True)


def clear_directory(directory):
    for filename in os.listdir(directory):
        if filename == '.gitkeep':  # Skip the .gitkeep file
            continue
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

        st.success(
            "El proceso de limpieza de datos ha terminado. En la siguiente pestaña puede proceder con la descarga de los datos estandarizados.")
    elif dataset == 'beneficiarios_fertilizantes_2023':
        data_cleaning2()
        st.success(
            "El proceso de limpieza de datos ha terminado. En la siguiente pestaña puede proceder con la descarga de los datos estandarizados.")


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
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2019-2022':
        st.markdown((
            """
                La siguiente aplicacion ha sido desarrollada para [SESNA](https://www.sesna.gob.mx/).
                El propósito de esta aplicación es la descarga, limpieza y unión de las bases de datos
                publicadas en los siguientes URLs para el Programa de Fertilizantes 2019-2022 [Beneficiarios 2019](https://datos.gob.mx/busca/dataset/programa-fertilizantes-2019), [Beneficiarios 2020](https://datos.gob.mx/busca/dataset/programa-fertilizantes-2020), [Beneficiarios 2021](https://datos.gob.mx/busca/dataset/programa-fertilizantes-2021), [Beneficiarios 2022](https://datos.gob.mx/busca/dataset/programa-fertilizantes-2022).
            """
        ))

    st.markdown("<br>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Suba el diccionario manual para empezar el proceso.")
    if uploaded_file is not None:
        # Check if the file is a CSV (or similar) before trying to read it
        if uploaded_file.name.endswith('.csv'):
            # Directly save the uploaded file to avoid modifying its content
            with open(os.path.join('data', uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getvalue())
            st.success(f"El archivo {uploaded_file.name} ha sido subido con éxito.")
        else:
            st.error("¡El archivo tiene que ser un .csv para continuar con el proceso!")

    session_state_with_love_mottum('footer')


def start_process():
    if st.session_state.main_page == 'Productores autorizados 2023':
        cols_button = st.columns([1, 1, 1])
        if cols_button[1].button('Descargar Listado Autorizados2023.', key='start_process_button'):
            data_download("https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-autorizados",
                          "data/productores_autorizados")
        session_state_with_love_mottum('footer1')
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        cols_button = st.columns([1, 1, 1])
        if cols_button[1].button('Descargar Listado Beneficiarios2023.', key='start_process_button'):
            data_download(
                "https://www.datos.gob.mx/busca/dataset/programa-de-fertilizantes-2023-listados-de-beneficiarios",
                "data/productores_beneficiarios")
        session_state_with_love_mottum('footer2')
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2019-2022':
        cols_button = st.columns([1, 1, 1])
        if cols_button[1].button('Descargar Listado Beneficiarios2019-2022.', key='start_process_button'):
            data_download("https://datos.gob.mx/busca/dataset/programa-fertilizantes-2019",
                          "data/productores_beneficiarios 2019-2022")
        session_state_with_love_mottum('footer22')


def data_download(url, download_destination_folder, progress_callback=None,
                  urls=[]):  # Exit the function if any required file is missing
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Directory 'data' missing, creating data directory.")
    if not os.path.exists('data/productores_autorizados'):
        os.makedirs('data/productores_autorizados')
        print("Directory 'data/productores_autorizados' missing, creating data/productores_autorizados.")
    if not os.path.exists('data/productores_beneficiarios'):
        os.makedirs('data/productores_beneficiarios')
        print("Directory 'data/productores_beneficiarios' missing, creating data/productores_beneficiarios.")
    if not os.path.exists('data/productores_beneficiarios 2019-2022'):
        os.makedirs('data/productores_beneficiarios 2019-2022')
        print(
            "Directory 'data/productores_beneficiarios 2019-2022' missing, creating data/productores_beneficiarios 2019-2022.")

    clear_directory('data/productores_autorizados')
    clear_directory('data/productores_beneficiarios')

    results = []
    datasets = []

    urls = ["https://datos.gob.mx/busca/dataset/programa-fertilizantes-2019",
            "https://datos.gob.mx/busca/dataset/programa-fertilizantes-2020",
            "https://datos.gob.mx/busca/dataset/programa-fertilizantes-2021",
            "https://datos.gob.mx/busca/dataset/programa-fertilizantes-2022"]
    with st.spinner(
            'Ejecutando scripts... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado!'):
        if st.session_state.main_page == 'Productores autorizados 2023':
            download_urls = scrape_urls(url)
        elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
            download_urls = scrape_urls(url)
        elif st.session_state.main_page == 'Beneficiarios fertilizantes 2019-2022':
            download_urls = []
            for url in [urls[0], urls[1], urls[2], urls[3]]:
                download_urls += scrape_xlsx(url)
        # Correctly initialize the progress bar with 0%
        # Calculate each step's progress increment based on the number of URLs
        progress_bar = st.progress(0)

        print('download_urls:', download_urls)
        print('results:', results)

        # Define the progress callback function
        def progress_callback(progress):
            progress_bar.progress(progress)

        result = download_datasets(download_urls, download_destination_folder, progress_callback)

        # Update progress to 100% after download_datasets completes
        # Explicitly set progress to 100% after all processing

        good_count = result['good_count']
        good_urls = result['good_urls']
        failed_count = result['failed_count']
        failed_urls = result['failed_urls']

        if good_count > 0:
            st.write(f"{good_count} datasets se han descargado de forma exitosa.")
            st.selectbox("URLs de los datasets descargados con éxito:", good_urls)
        else:
            st.write(
                "No se pudo descargar ningún dataset de: ${download_urls[0]}")

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

        logger.info("Fin de Ejecución")
        st.write(
            "Pasando archivos .xlsx a .csv... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado...")
        convert_xlsx_to_csv_in_directory('data/productores_beneficiarios 2019-2022')
        st.success(
            "El proceso de descarga ha terminado. En la siguiente pestaña puede proceder con la limpieza de los datos."
        )


def clean_data_screen():
    if st.session_state.main_page == 'Productores autorizados 2023':
        required_files = [
            'data/dataset_inegi.csv',
            'data/Diccionario_manual.csv'
        ]

        listado_productores, rowSum = load_datasets('data/productores_autorizados/')

        stats = {
            'Número de filas': [rowSum],
            'Número de columnas': [listado_productores.shape[1]],
            # Add more statistics here if needed
        }
        stats_df = pd.DataFrame(stats)
        # Display statistics
        st.markdown("""
        <style>
        .centered {
            font-size: 15px; /* Adjust the size as needed */
            font-weight: bold; /* Makes the text bold */
            /* Add more styling as needed */
        }
        </style>
        <div class="centered">Current dataset</div>
        """, unsafe_allow_html=True)

        st.table(stats_df)

        with st.spinner(
                'Ejecutando scripts... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado!'
        ):
            cols_button = st.columns([1, 1, 1])
            if cols_button[1].button('Limpieza de datos de Listado Productores2023.', key='start_process_button'):
                data_cleaning_function('productores_autorizados_2023')
                # st.success("El proceso de limpieza de datos ha terminado. En la siguiente pestaña puede proceder con la descarga de los datos estandarizados.")
            session_state_with_love_mottum('footer4')
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        required_files = [
            'data/dataset_inegi.csv',
            'data/Diccionario_Simple.csv'
        ]
        listado_beneficiarios, rowSum = load_datasets('data/productores_beneficiarios/')

        stats = {
            'Número de filas': [rowSum],
            'Número de columnas': [listado_beneficiarios.shape[1]],
            # Add more statistics here if needed
        }
        stats_df = pd.DataFrame(stats)
        # Display statistics
        st.markdown("""
        <style>
        .centered {
            font-size: 15px; /* Adjust the size as needed */
            font-weight: bold; /* Makes the text bold */
            /* Add more styling as needed */
        }
        </style>
        <div class="centered">Current dataset</div>
        """, unsafe_allow_html=True)

        st.table(stats_df)

        with st.spinner(
                'Ejecutando scripts... Esto puede tardar unos minutos. No cambie de pestaña hasta que el proceso haya acabado!'
        ):
            cols_button = st.columns([1, 1, 1])
            if cols_button[1].button('Limpieza de datos de Listado Beneficiarios2023.', key='start_process_button'):
                data_cleaning_function('beneficiarios_fertilizantes_2023')
            session_state_with_love_mottum('footer5')

    missing_files = [file for file in required_files if not os.path.exists(file)]

    if missing_files:
        # Display an error message for each missing file
        for missing_file in missing_files:
            st.error(
                f"Error: El archivo requerido {missing_file} no ha sido subido todavía, vuelva a la introducción y súbalo desde ahi.")
        return


def show_finished():
    if st.session_state.main_page == 'Productores autorizados 2023':
        dataset_path = "data/listado_productores_complete2023.csv"
        if os.path.exists(dataset_path):
            st.markdown("""
            <style>
            .centered {
                text-align: center;
                font-size: 20px; /* Adjust the size as needed */
                font-weight: bold; /* Makes the text bold */
                /* Add more styling as needed */
            }
            </style>
            <div class="centered">¡El dataset está listo!</div>
            """, unsafe_allow_html=True)
            # Load dataset to calculate statistics
            df = pd.read_csv(dataset_path)
            # Calculate statistics
            stats = {
                'Número de filas': [df.shape[0]],
                'Número de columnas': [df.shape[1]],
                # Add more statistics here if needed
            }
            stats_df = pd.DataFrame(stats)
            # Display statistics
            st.markdown("""
            <style>
            .centered {
                font-size: 15px; /* Adjust the size as needed */
                font-weight: bold; /* Makes the text bold */
                /* Add more styling as needed */
            }
            </style>
            <div class="centered">Final dataset</div>
            """, unsafe_allow_html=True)

            st.table(stats_df)

            cols = st.columns([1, 2, 1])
            with open(dataset_path, "rb") as file:
                cols[1].download_button(
                    label="Pulsa para acceder al dataset completo.",
                    data=file,
                    file_name="listado_productores_completo2023.csv",
                    mime="text/csv",
                )
            session_state_with_love_mottum('footer6')
        else:
            st.error("¡Necesitas ejecutar el proceso antes de venir a esta pantalla!")
            session_state_with_love_mottum('footer7')

    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        dataset_path = "data/LISTADO_BENEFICIARIOS2023_COMPLETO.csv"
        if os.path.exists(dataset_path):
            st.markdown("""
            <style>
            .centered {
                text-align: center;
                font-size: 20px; /* Adjust the size as needed */
                font-weight: bold; /* Makes the text bold */
                /* Add more styling as needed */
            }
            </style>
            <div class="centered">¡El dataset está listo!</div>
            """, unsafe_allow_html=True)
            # Load dataset to calculate statistics
            df = pd.read_csv(dataset_path)
            # Calculate statistics
            stats = {
                'Número de filas': [df.shape[0]],
                'Número de columnas': [df.shape[1]],
                # Add more statistics here if needed
            }
            stats_df = pd.DataFrame(stats)
            # Display statistics
            st.markdown("""
            <style>
            .centered {
                font-size: 15px; /* Adjust the size as needed */
                font-weight: bold; /* Makes the text bold */
                /* Add more styling as needed */
            }
            </style>
            <div class="centered">Final dataset</div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.table(stats_df)

            cols = st.columns([1, 2, 1])
            with open(dataset_path, "rb") as file:
                cols[1].download_button(
                    label="Pulsa aquí para acceder al dataset completo.",
                    data=file,
                    file_name="LISTADO_BENEFICIARIOS2023_COMPLETO.csv",
                    mime="text/csv",
                )
            session_state_with_love_mottum('footer8')

        else:
            st.markdown(
                "<h2 style='text-align: center;'>Necesitas ejecutar el proceso antes de venir a esta pantalla.</h2>",
                unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            cols = st.columns([1, 1, 1])
            cols[1].image('docs/images/mottum.svg', use_column_width=True)  # Colocar la imagen en la columna del medio


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
        st.session_state.main_page = om('Main menu',
                                        ['Productores autorizados 2023', 'Beneficiarios fertilizantes 2023',
                                         'Beneficiarios fertilizantes 2019-2022'],
                                        icons=["list-task", "list-task", "list-task"], menu_icon="cast")
    if st.session_state.main_page == 'Productores autorizados 2023':
        if 'sub_page' not in st.session_state:
            st.session_state.sub_page = '1. Introducción'
        st.session_state.sub_page = st.radio('Productores autorizados 2023',
                                             ['1. Introducción', '2. Descarga y Transformación', '3. Limpieza de datos',
                                              '4. Acceso a las tablas de resultados [.csv]'])
        if st.session_state.sub_page == '1. Introducción':
            show_intro()
        elif st.session_state.sub_page == '2. Descarga y Transformación':
            start_process()
        elif st.session_state.sub_page == '3. Limpieza de datos':
            clean_data_screen()
        elif st.session_state.sub_page == '4. Acceso a las tablas de resultados [.csv]':
            show_finished()
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2023':
        if 'second_sub_page' not in st.session_state:
            st.session_state.second_sub_page = '1. Introducción'
        st.session_state.second_sub_page = st.radio('Beneficiarios fertilizantes 2023',
                                                    ['1. Introducción', '2. Descarga y Transformación',
                                                     '3. Limpieza de datos',
                                                     '4. Acceso a las tablas de resultados [.csv]'])
        if st.session_state.second_sub_page == '1. Introducción':
            show_intro()
        elif st.session_state.second_sub_page == '2. Descarga y Transformación':
            start_process()
        elif st.session_state.second_sub_page == '3. Limpieza de datos':
            clean_data_screen()
        elif st.session_state.second_sub_page == '4. Acceso a las tablas de resultados [.csv]':
            show_finished()
    elif st.session_state.main_page == 'Beneficiarios fertilizantes 2019-2022':
        if 'third_sub_page' not in st.session_state:
            st.session_state.third_sub_page = '1. Introducción'
        st.session_state.third_sub_page = st.radio('Beneficiarios fertilizantes 2019-2022',
                                                   ['1. Introducción', '2. Descarga y Transformación',
                                                    '3. Limpieza de datos',
                                                    '4. Acceso a las tablas de resultados [.csv]'])
        if st.session_state.third_sub_page == '1. Introducción':
            show_intro()
        elif st.session_state.third_sub_page == '2. Descarga y Transformación':
            start_process()
        elif st.session_state.third_sub_page == '3. Limpieza de datos':
            clean_data_screen()
        elif st.session_state.third_sub_page == '4. Acceso a las tablas de resultados [.csv]':
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
