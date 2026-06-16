from pathlib import Path
import pandas as pd


def leer_excel(nombre_archivo):
    # 1. Nos paramos en 'src/utilidades'
    directorio_actual = Path(__file__).resolve().parent

    # 2. Subimos DOS niveles: primero a 'src', luego a la raíz del proyecto
    raiz_proyecto = directorio_actual.parent.parent

    # 3. Ahora sí entramos a 'files' desde la raíz
    ruta_excel = raiz_proyecto / "files" / nombre_archivo

    print(f"Buscando en la ruta real: {ruta_excel}\n")

    if ruta_excel.exists():
        try:
            df = pd.read_excel(ruta_excel)
            print("¡Archivo leído con éxito!")
            print("-" * 40)
            print(df.head())  # Muestra las primeras filas
            print("-" * 40)
            return df
        except Exception as e:
            print(f"Error al leer el archivo Excel: {e}")
            return None
    else:
        print(f"[ERROR] El archivo no existe en esa ubicación.")
        return None


if __name__ == "__main__":
    # Pon aquí el nombre exacto de tu archivo
    archivo_a_cargar = "BSD_Grebo_UCI_2025_adultos.xlsx"

    leer_excel(archivo_a_cargar)