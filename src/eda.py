import os
import glob
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from fuzzywuzzy import process

def load_datasets(directory):
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    dataframes = [pd.read_csv(file, encoding='cp1252', index_col=0, skiprows=1) for file in csv_files]
    merged_df = pd.concat(dataframes, join='inner', ignore_index=True)
    return merged_df

def clean_text(text):
    text = text.str.strip()
    text = text.str.lower()
    text = text.str.replace('\s+', ' ')
    text = text.str.replace('^\s+|\s+?$', '')
    return text

def create_mapping_dict(df, column, unique_values):
    return {
        value: matches[0][0] if len(matches) == 1 or matches[0][1] != matches[1][1] else value
        for value in df[column].unique() if isinstance(value, str)
        for matches in [process.extract(value, unique_values.tolist(), limit=1)]
    }

def main():
    inegi_df = pd.read_csv('data/dataset_inegi.csv', encoding='cp1252', index_col=0)
    df = load_datasets("data/fertilizantes_autorizados")

    df = df.drop_duplicates()

    for col in ['ESTADO', 'MUNICIPIO']:
        df[col] = clean_text(df[col]).str.title()

    unique_values_df = pd.DataFrame({
        'ESTADO': pd.Series(df['ESTADO'].unique()),
        'MUNICIPIO': pd.Series(df['MUNICIPIO'].unique()),
        'NOM_ENT': pd.Series(inegi_df['NOM_ENT'].unique()),
        'NOM_MUN': pd.Series(inegi_df['NOM_MUN'].unique())
    })

    estado_to_nom_ent = create_mapping_dict(df, 'ESTADO', unique_values_df['NOM_ENT'])
    municipio_to_nom_mun = create_mapping_dict(df, 'MUNICIPIO', unique_values_df['NOM_MUN'])

    df['ESTADO'] = df['ESTADO'].map(estado_to_nom_ent)
    df['MUNICIPIO'] = df['MUNICIPIO'].map(municipio_to_nom_mun)

    df = df.sort_values('ESTADO', ascending=True)

    df.to_csv('data/productores_autorizados_fertilizantes.csv', index=False)

if __name__ == "__main__":
    main()