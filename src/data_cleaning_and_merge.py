import pandas as pd
import seaborn as sns
from thefuzz import fuzz
from thefuzz import process
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import re
import unidecode


# Definición de funciones

def load_datasets(directory):
    # Get a list of all CSV files in the directory
    csv_files = glob.glob(os.path.join(directory, '*.csv'))

    # Read each CSV file and store the DataFrame in a list
    dataframes = [pd.read_csv(file, encoding='cp1252', index_col=0, skiprows=1) for file in csv_files]

    # Concatenate all DataFrames in the list
    merged_df = pd.concat(dataframes, join='inner', ignore_index=True)

    return merged_df


def clean_text(text):
    """
    De esta manera tenemos el texto sin espacios blancos extra y sobre todo con todas las palabras con capitalización correcta.
    """
    if pd.isna(text):
        return text
    text = text.strip()  # Eliminate white spaces
    text = text.lower()  # Convert to lowercase
    text = unidecode.unidecode(text)  # Remove accents
    text = re.sub('-.*-', '', text)
    text = re.sub('\s+', ' ', text)  # Eliminate extra white spaces
    text = re.sub('^\s+|\s+?$', '', text)  # Eliminate spaces at the beginning and end
    return text


# Crear una función para encontrar la mejor coincidencia difusa con límites entre 90 y 100 de coincidencia
def fuzzy_merge(df_inegi, df_prod, key1, key2, threshold=96, limit=1):
    """
    df_inegi: DataFrame de la izquierda (el DataFrame principal)
    df_prod: DataFrame de la derecha (el DataFrame con el que se quiere hacer el join)
    key1: Columna de la clave en df_inegi
    key2: Columna de la clave en df_prod
    threshold: Umbral de coincidencia difusa
    limit: Número de coincidencias a encontrar
    """
    s = df_prod[key2].tolist()

    # Encontrar las mejores coincidencias para cada clave en df_inegi
    matches = df_inegi[key1].apply(lambda x: process.extractOne(x, s, score_cutoff=threshold))

    # Crear una columna con las mejores coincidencias
    df_inegi['best_match'] = [match[0] if match else None for match in matches]
    df_inegi['match_score'] = [match[1] if match else None for match in matches]

    # Hacer el merge con las mejores coincidencias
    df_merged = pd.merge(df_inegi, df_prod, left_on='best_match', right_on=key2, how='inner',
                         suffixes=('_inegi', '_prod'))

    return df_merged


def drop_columns(df, columns_to_drop):
    df = df.drop(columns_to_drop, axis=1)
    return df


def drop_duplicates(df):
    df = df.drop_duplicates()
    return df


def save_to_csv(df, filename):
    df.to_csv(filename, index=False)


def main():
    path_dataset_inegi = 'data/dataset_inegi.csv'
    dataset_inegi = pd.read_csv(path_dataset_inegi, encoding='cp1252')

    listado_productores = load_datasets('data/productores_autorizados/')

    # Eliminamos las columnas que no son de interés
    COLUMNS_TO_DROP = ['MAPA', 'Estatus', 'NOM_ABR', 'CVE_LOC', 'NOM_LOC', 'AMBITO', 'LATITUD', 'LONGITUD',
                       'LAT_DECIMAL', 'LON_DECIMAL', 'ALTITUD', 'CVE_CARTA', 'POB_TOTAL',
                       'POB_MASCULINA', 'POB_FEMENINA', 'TOTAL DE VIVIENDAS HABITADAS']
    dataset_inegi = drop_columns(dataset_inegi, COLUMNS_TO_DROP)

    dataset_inegi_clean = drop_duplicates(dataset_inegi)

    # Crear una columna única para la clave de municipio
    dataset_inegi_clean['CVE_MUN_Unique'] = dataset_inegi_clean['CVE_ENT'].astype(str) + '-' + dataset_inegi_clean[
        'CVE_MUN'].astype(str)

    # Estandarizamos la limpieza de los datos en el dataset de INEGI
    dataset_inegi_clean['NOM_ENT_Clean'] = dataset_inegi_clean['NOM_ENT'].apply(clean_text)
    dataset_inegi_clean['NOM_MUN_Clean'] = dataset_inegi_clean['NOM_MUN'].apply(clean_text)

    # Solo las dos primeras columnas de lista_productores.
    Estados_productores = listado_productores[['ESTADO', 'MUNICIPIO']]

    Estados_productores = drop_duplicates(Estados_productores)

    # Estandarizamos la limpieza de los datos para el dataset de productores.
    Estados_productores['ESTADO_Clean'] = Estados_productores['ESTADO'].apply(clean_text)
    Estados_productores['MUNICIPIO_Clean'] = Estados_productores['MUNICIPIO'].apply(clean_text)

    # Primero creemos una columna clave en cada dataset -> Estados productores

    Estados_productores["ESTADO_Clean"] = Estados_productores["ESTADO_Clean"].astype(str)
    Estados_productores["MUNICIPIO_Clean"] = Estados_productores["MUNICIPIO_Clean"].astype(str)

    Estados_productores["KEY_prod"] = Estados_productores["ESTADO_Clean"] + "-" + Estados_productores["MUNICIPIO_Clean"]

    # Primero creemos una columna clave en cada dataset -> INEGI

    dataset_inegi_clean["NOM_ENT_Clean"] = dataset_inegi_clean["NOM_ENT_Clean"].astype(str)
    dataset_inegi_clean["NOM_MUN_Clean"] = dataset_inegi_clean["NOM_MUN_Clean"].astype(str)
    dataset_inegi_clean['CVE_ENT'] = dataset_inegi_clean['CVE_ENT'].astype(str)
    dataset_inegi_clean['CVE_MUN'] = dataset_inegi_clean['CVE_MUN'].astype(str)

    dataset_inegi_clean["KEY_inegi"] = dataset_inegi_clean["NOM_ENT_Clean"] + "-" + dataset_inegi_clean["NOM_MUN_Clean"]

    Estados_productores = Estados_productores.drop(['ESTADO', 'MUNICIPIO'], axis=1)
    Estados_productores = drop_duplicates(Estados_productores)

    # Aplicar la función de coincidencia difusa
    diccionario = fuzzy_merge(dataset_inegi_clean, Estados_productores, 'KEY_inegi', 'KEY_prod')

    diccionario = diccionario[['CVE_ENT', 'NOM_ENT', 'CVE_MUN', 'NOM_MUN', 'KEY_prod']]
    diccionario['CVE_ENT'] = diccionario['CVE_ENT'].astype(str)
    diccionario['CVE_MUN'] = diccionario['CVE_MUN'].astype(str)
    print(diccionario['CVE_ENT'].unique())

    save_to_csv(diccionario, 'data/merged_dataset.csv')

    # Crear una variable KEY en listado de productores y el diccionario para hacer el join
    listado_productores['ESTADO_Clean'] = listado_productores['ESTADO'].apply(clean_text)
    listado_productores['MUNICIPIO_Clean'] = listado_productores['MUNICIPIO'].apply(clean_text)
    listado_productores['Estado-mun-KEY'] = listado_productores['ESTADO_Clean'].astype(str) + '-' + listado_productores[
        'MUNICIPIO_Clean'].astype(str)

    diccionario_Sin_VC = diccionario[diccionario["NOM_ENT"] != "Veracruz de Ignacio de la Llave"]

    diccionario_manipulado = pd.read_csv('data/Diccionario_manual.csv', encoding='cp1252')

    # Hacer el join
    listado_productores_complete = pd.merge(listado_productores, diccionario, left_on="Estado-mun-KEY",
                                        right_on="KEY_prod", how='left', suffixes=('_prod', '_inegi'))
    
    print(listado_productores['Estado-mun-KEY'].unique())
    print(diccionario_manipulado['KEY_prod'].unique())
    print(listado_productores_complete.columns)

    #print(listado_productores_complete['NOM_MUN'].unique())

    
    #listado_productores_complete[['CVE_ENT', 'CVE_MUN']] = listado_productores_complete['CVE_MUN_Unique'].str.split('-',expand=True)
    listado_productores_complete = listado_productores_complete[
        ['ESTADO', 'MUNICIPIO', 'NOM_MUN', 'NOM_ENT', 'CVE_ENT', 'CVE_MUN', 'ACUSE', 'APELLIDO PATERNO',
         'APELLIDO MATERNO', 'NOMBRE (S)', 'PAQUETE', 'KEY_prod']]
    print(listado_productores_complete['CVE_ENT'].unique())
    # Los nombres y apellidos paternos y maternos que están vacíos y tengan número de acuse se reemplazarán por 'unknown'
    listado_productores_complete.loc[(listado_productores_complete['APELLIDO PATERNO'].isna()) & (
        listado_productores_complete['ACUSE'].notna()), 'APELLIDO PATERNO'] = 'unknown'
    listado_productores_complete.loc[(listado_productores_complete['APELLIDO MATERNO'].isna()) & (
        listado_productores_complete['ACUSE'].notna()), 'APELLIDO MATERNO'] = 'unknown'
    listado_productores_complete.loc[
        (listado_productores_complete['NOMBRE (S)'].isna()) & (listado_productores_complete['ACUSE'].notna()), 'NOMBRE (S)'] = 'unknown'
    
    listado_productores_complete = listado_productores_complete.astype({
    'ESTADO': 'str',
    'MUNICIPIO': 'str',
    'ACUSE': 'str',
    'APELLIDO PATERNO': 'str',
    'APELLIDO MATERNO': 'str',
    'NOMBRE (S)': 'str',
    'PAQUETE': 'int',
    'NOM_MUN': 'str',
    'NOM_ENT': 'str',
    'CVE_MUN': 'str',
    'CVE_ENT': 'str',
    'KEY_prod': 'str'

    })

    listado_productores_complete = listado_productores_complete.rename(columns={
    'ESTADO': 'estado1',
    'MUNICIPIO': 'municipio1',
    'ACUSE': 'acuse',
    'APELLIDO PATERNO': 'apellido_paterno',
    'APELLIDO MATERNO': 'apellido_materno',
    'NOMBRE (S)': 'nombre_propio',
    'PAQUETE': 'paquete',
    'NOM_MUN': 'municipio',
    'NOM_ENT': 'entidad',
    'CVE_MUN': 'cve_mun',
    'CVE_ENT': 'cve_ent',
    'KEY_prod': 'key_prod'
    })

    listado_productores_complete = listado_productores_complete.drop(columns=['estado1', 'municipio1'])

    listado_productores_complete['id'] = listado_productores_complete.index

    # Assuming df is your DataFrame
    ordered_columns = ['id', 'cve_ent', 'entidad', 'cve_mun', 'municipio', 'acuse', 'apellido_paterno', 'apellido_materno', 'nombre_propio', 'paquete', 'key_prod']
    listado_productores_complete = listado_productores_complete.reindex(columns=ordered_columns)
    
    listado_productores_complete['cve_ent'] = listado_productores_complete['cve_ent'].str.zfill(2)
    listado_productores_complete['cve_mun'] = listado_productores_complete['cve_mun'].str.zfill(3)

    save_to_csv(listado_productores_complete, 'data/merged_dataset.csv')


if __name__ == "__main__":
    main()
