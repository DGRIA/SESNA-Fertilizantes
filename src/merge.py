import pandas as pd

def load_datasets():
    dtype_dict = {
        'CVE_ENT': str,
        'CVE_MUN': str
    }

    inegi_df = pd.read_csv('data/dataset_inegi.csv', encoding='cp1252', dtype=dtype_dict)
    inegi_df.drop(columns=['MAPA'], inplace=True)
    acreditados_df = pd.read_csv('data/productores_autorizados_fertilizantes.csv')
    
    return inegi_df, acreditados_df

def create_mapping(inegi_df, acreditados_df, inegi_column, inegi_column2, acreditados_column, new_column):
    mapping_dict = inegi_df.set_index(inegi_column)[inegi_column2].to_dict()
    acreditados_df[new_column] = acreditados_df[acreditados_column].map(mapping_dict)

def rename_columns(acreditados_df):
    final_column_names = {
        'ESTADO': 'estado',
        'MUNICIPIO': 'municipio',
        'ACUSE': 'acuse',
        'APELLIDO PATERNO': 'apellido_paterno',
        'APELLIDO MATERNO': 'apellido_materno',
        'NOMBRE (S)': 'nombre_propio',
        'PAQUETE': 'paquete',
    }
    acreditados_df.rename(columns=final_column_names, inplace=True)

def change_column_types(acreditados_df):
    acreditados_df['estado'] = acreditados_df['estado'].astype(str)
    acreditados_df['municipio'] = acreditados_df['municipio'].astype(str)
    acreditados_df['acuse'] = acreditados_df['acuse'].astype(str)
    acreditados_df['apellido_paterno'] = acreditados_df['apellido_paterno'].astype(str)
    acreditados_df['apellido_materno'] = acreditados_df['apellido_materno'].astype(str)
    acreditados_df['nombre_propio'] = acreditados_df['nombre_propio'].astype(str)
    acreditados_df['paquete'] = acreditados_df['paquete'].astype(int)
    acreditados_df['cve_ent'] = acreditados_df['cve_ent'].astype(str)
    acreditados_df['cve_mun'] = acreditados_df['cve_mun'].astype(str)

def save_to_csv(acreditados_df):
    acreditados_df.to_csv('data/productores_autorizados_final.csv', index=False)

def main():
    inegi_df, acreditados_df = load_datasets()
    create_mapping(inegi_df, acreditados_df, 'NOM_ENT', 'CVE_ENT', 'ESTADO', 'cve_ent')
    create_mapping(inegi_df, acreditados_df, 'NOM_MUN', 'CVE_MUN', 'MUNICIPIO', 'cve_mun')
    rename_columns(acreditados_df)
    change_column_types(acreditados_df)
    save_to_csv(acreditados_df)

if __name__ == "__main__":
    main()