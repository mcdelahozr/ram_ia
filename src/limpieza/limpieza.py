import numpy as np

def eliminar_filas_con_nan(df_adultos):
    """
    Elimina las filas que contienen valores NaN en el DataFrame.
    
    Parámetros:
    data (pd.DataFrame): El DataFrame del cual se eliminarán las filas con NaN.
    
    Retorna:
    pd.DataFrame: Un nuevo DataFrame sin las filas que contienen NaN.
    """
    # Identify columns that are entirely NaN
    columns_all_nan = df_adultos.columns[df_adultos.isnull().all()].tolist()

    # Identify columns where all non-NaN values are False
    columns_all_false = []
    for col in df_adultos.columns:
        # Check if the column contains any non-NaN values
        if df_adultos[col].count() > 0:
            # Check if all non-NaN values are False
            if (df_adultos[col].dropna() == False).all():
                columns_all_false.append(col)

    #print(f"Columns with all NaN values: {columns_all_nan}")
    #print(f"Columns with all non-NaN values as False: {columns_all_false}")

    # Combine the lists and remove duplicates
    columns_to_consider_for_dropping = list(set(columns_all_nan + columns_all_false))
    #print(f"\nCombined list of columns to consider for dropping (empty or all False): {columns_to_consider_for_dropping}")
    #print(f"Number of such columns: {len(columns_to_consider_for_dropping)}")
    return df_adultos.drop(columns=columns_to_consider_for_dropping)
