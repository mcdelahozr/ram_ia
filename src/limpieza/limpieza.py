"""
Módulo de limpieza para BSD_Grebo_UCI_2025_adultos.xlsx.

Pasos del pipeline:
  1. Lectura con header correcto (fila 0 del Excel está vacía; encabezados en fila 1).
  2. Eliminación de las 4 filas corruptas (País != 'COL').
  3. Eliminación de la primera serie de antibióticos (columnas vacías, índices 41-82).
  4. Renombrado: sufijos .1 de la segunda serie → nombre canónico.
  5. Eliminación de columnas 100 % nulas / 100 % False y, opcionalmente,
     columnas por encima de un umbral de nulos (umbral_nulos), respetando
     las columnas clínicas de importancia definidas en _COLUMNAS_CLINICAS.
  6. Clasificación R / S / ambiguo usando umbrales de Antibioticos.xlsx.
"""

import re
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------------

_RAIZ = Path(__file__).resolve().parent.parent.parent
_FILES = _RAIZ / "files"


# ---------------------------------------------------------------------------
# Columnas clínicas protegidas del umbral de nulos
# ---------------------------------------------------------------------------

# Estas columnas tienen alta proporción de nulos pero son marcadores clínicos
# relevantes. Se protegen del umbral de nulos configurable; solo se eliminan
# si tienen 100 % de nulos (sin datos reales).
_COLUMNAS_CLINICAS = frozenset({
    "BLEE",
    "Beta-lactamasa",
    "Carbapenemase",
    "MRSA",
    "Resistencia inducible a la clindamicina",
    "EDTA",
    "Acido Boronico",
    "Rapidec Carba NP",
})


# ---------------------------------------------------------------------------
# 0. Lectura
# ---------------------------------------------------------------------------

def leer_datos_principales() -> pd.DataFrame:
    """
    Lee BSD_Grebo_UCI_2025_adultos.xlsx.
    El Excel tiene una fila vacía en la posición 0; los encabezados reales
    están en la fila 1 (0-indexado), por eso se usa header=1.
    """
    ruta = _FILES / "BSD_Grebo_UCI_2025_adultos.xlsx"
    return pd.read_excel(ruta, header=1)


def leer_antibioticos() -> pd.DataFrame:
    """Tabla de referencia con códigos y umbrales de resistencia (CMI ≥ X → R)."""
    return pd.read_excel(_FILES / "Antibioticos.xlsx")


def leer_resistencia() -> pd.DataFrame:
    """
    Lee Resistencia.xlsx.
    Misma estructura que el archivo principal: fila 0 vacía, encabezados en fila 1.
    """
    ruta = _FILES / "Resistencia.xlsx"
    return pd.read_excel(ruta, header=1)


# ---------------------------------------------------------------------------
# 1. Filas corruptas
# ---------------------------------------------------------------------------

def eliminar_filas_corruptas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina las 4 filas donde 'País' != 'COL'.
    Estas filas tienen un corrimiento de columnas evidente:
      - País = 'Orina', Fecha de muestra = 2026-12-31, Categoría de edad = '-'.
    Todas pertenecen al mismo paciente (ID 19499257).
    """
    return df[df["País"] == "COL"].reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. Primera serie de antibióticos (vacía)
# ---------------------------------------------------------------------------

# Columnas 41-82 del Excel: primera serie de antibióticos, todas 100 % nulas.
# Son un artefacto de la estructura del archivo (doble encabezado en el Excel).
_PRIMERA_SERIE = frozenset({
    "AMK", "AMX", "AMC", "AMP", "SAM", "ATM", "CEP", "CZO", "FEP", "CSL",
    "CTX", "CTT", "FOX", "CAZ", "CRO", "CIP", "CLI", "CHL", "ERY", "FLU",
    "GEN", "IPM", "LVX", "LNZ", "MEM", "MTR", "MFX", "NIT", "OXA", "PEN",
    "PIP", "TZP", "QDA", "RIF", "TCY", "TCC", "TGC", "SXT", "VAN", "FCT",
    "NAL", "AMB",
})


def eliminar_primera_serie_antibioticos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina las columnas de la primera serie de antibióticos.
    Solo borra una columna si su nombre está en la lista Y está 100 % vacía,
    para no afectar accidentalmente columnas con datos del mismo nombre.
    """
    cols_eliminar = [
        c for c in df.columns
        if c in _PRIMERA_SERIE and df[c].isnull().all()
    ]
    return df.drop(columns=cols_eliminar)


# ---------------------------------------------------------------------------
# 3. Renombrado de columnas con sufijo .1
#    (se hace ANTES de la eliminación por umbral para que las columnas
#     renombradas queden expuestas al filtro de nulos correctamente)
# ---------------------------------------------------------------------------

def renombrar_columnas_duplicadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombra las columnas con sufijo '.1' a su nombre canónico.
    Solo renombra si el nombre base ya no existe en el DataFrame,
    lo que está garantizado después de eliminar la primera serie vacía.
    Las columnas '.2' quedan intactas (su nombre base ya existe tras el renombrado).
    """
    mapa = {}
    for col in df.columns:
        if col.endswith(".1"):
            nombre_base = col[:-2]
            if nombre_base not in df.columns:
                mapa[col] = nombre_base
    return df.rename(columns=mapa)


# ---------------------------------------------------------------------------
# 4. Eliminación de columnas vacías y por umbral de nulos
# ---------------------------------------------------------------------------

def eliminar_columnas_vacias(
    df: pd.DataFrame,
    umbral_nulos: float = 1.0,
) -> pd.DataFrame:
    """
    Elimina columnas según dos criterios:

    a) Siempre: columnas con 100 % de nulos o cuyos únicos valores no-NaN
       son False (flags sin información real). Este criterio ignora la
       protección clínica — si no hay ningún dato, la columna no aporta nada.

    b) Por umbral (si umbral_nulos < 1.0): columnas cuyo porcentaje de nulos
       es >= umbral_nulos. Las columnas definidas en _COLUMNAS_CLINICAS están
       protegidas de este segundo criterio aunque superen el umbral.

    Parámetros
    ----------
    df            : DataFrame a limpiar.
    umbral_nulos  : Fracción [0.0 – 1.0]. Por defecto 1.0 (solo 100 % nulas).
                    Ejemplo: 0.90 elimina columnas con >= 90 % de nulos.
    """
    # ── a) Eliminación absoluta (100 % nulos o 100 % False) ──────────────────
    cols_null_total = [c for c in df.columns if df[c].isnull().all()]
    cols_all_false = [
        c for c in df.columns
        if c not in cols_null_total
        and df[c].count() > 0
        and (df[c].dropna() == False).all()
    ]
    cols_eliminar = set(cols_null_total + cols_all_false)

    # ── b) Eliminación por umbral (respetando columnas clínicas) ─────────────
    if umbral_nulos < 1.0:
        pct_nulos = df.isnull().mean()
        cols_umbral = [
            c for c in df.columns
            if pct_nulos[c] >= umbral_nulos
            and c not in _COLUMNAS_CLINICAS
            and c not in cols_eliminar
        ]
        cols_eliminar.update(cols_umbral)

    return df.drop(columns=list(cols_eliminar))


# ---------------------------------------------------------------------------
# 5. Normalización y clasificación de CMI
# ---------------------------------------------------------------------------

_RE_CMI = re.compile(r"^([><=]+)?\s*(\d+\.?\d*|\.\d+)$")


def parsear_cmi(valor) -> tuple:
    """
    Convierte un valor CMI (string o numérico) en (operador, valor_float).

    Ejemplos:
      ">16"    → (">",  16.0)
      "<=.125" → ("<=", 0.125)
      "4"      → ("=",  4.0)
      "R"      → ("R",  nan)    — resistente cualitativo
      "S"      → ("S",  nan)    — sensible cualitativo
      "I"      → ("I",  nan)    — intermedio cualitativo
      NaN      → (None, nan)
    """
    if pd.isna(valor) or valor is False or str(valor).strip() in ("False", ""):
        return (None, np.nan)

    s = str(valor).strip()

    if s.upper() == "R":
        return ("R", np.nan)
    if s.upper() == "S":
        return ("S", np.nan)
    if s.upper() == "I":
        return ("I", np.nan)

    m = _RE_CMI.match(s)
    if m:
        op = m.group(1) or "="
        return (op, float(m.group(2)))

    return (None, np.nan)


def cmi_a_float(valor) -> float:
    """Extrae solo el valor numérico de un CMI (descarta el operador)."""
    _, val = parsear_cmi(valor)
    return val


def _extraer_umbral(texto: str) -> float:
    """
    Obtiene el primer número de una celda de umbral como '≥ 16' o '≥ 32/16'.
    """
    numeros = re.findall(r"\d+\.?\d*", str(texto))
    return float(numeros[0]) if numeros else np.nan


def _clasificar_un_cmi(valor, umbral: float) -> str | None:
    """
    Devuelve 'R', 'S' o None (ambiguo/sin dato) dado un valor CMI y el umbral.

    Criterio principal: CMI ≥ umbral → Resistente.

    Manejo de operadores:
      "=val"  → comparación directa con el umbral.
      ">val"  → CMI real > val. Se clasifica como R cuando:
                  · val >= umbral  (ya supera el umbral directamente), o
                  · val * 2 >= umbral  (la siguiente dilución estándar alcanza
                    el umbral; ej. >32 con umbral 64: 32×2 = 64 ≥ 64 → R).
                Fuera de estos casos, el resultado es ambiguo (None).
      "<=val" → CMI real ≤ val. S cuando val < umbral; ambiguo si val >= umbral.
      "R"/"S" → resultado cualitativo directo.
    """
    if np.isnan(umbral):
        return None

    op, val = parsear_cmi(valor)

    if op == "R":
        return "R"
    if op == "S":
        return "S"
    if op is None or (isinstance(val, float) and np.isnan(val)):
        return None
    if op == "=":
        return "R" if val >= umbral else "S"
    if op in (">", ">="):
        if val >= umbral:
            return "R"
        # Heurística de siguiente dilución: en microbiología, los valores se
        # reportan en diluciones dobles (1, 2, 4, 8...). Si ">val" y la
        # siguiente dilución (val*2) alcanza el umbral, se clasifica como R.
        if op == ">" and val * 2 >= umbral:
            return "R"
        return None
    if op in ("<", "<="):
        return "S" if val < umbral else None

    return None


def clasificar_resistencia(
    df: pd.DataFrame,
    df_antibioticos: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrega una columna '{codigo}_res' ('R' / 'S' / NaN) por cada antibiótico
    que tenga umbral definido en df_antibioticos y columna CMI presente en df.

    Notas:
    - df_antibioticos debe tener columnas 'Código' y 'Resistente (R)'.
    - Cuando un código aparece más de una vez (ej. CZO sistémico/urinario)
      se conserva el primer umbral (generalmente el más bajo, más conservador).
    - NaN en la columna '_res' indica valor ausente o resultado ambiguo.
    """
    umbrales: dict[str, float] = {}
    for _, fila in df_antibioticos.iterrows():
        codigo = str(fila["Código"]).strip()
        if codigo not in umbrales:
            umbrales[codigo] = _extraer_umbral(str(fila.get("Resistente (R)", "")))

    df = df.copy()
    for codigo, umbral in umbrales.items():
        if codigo in df.columns:
            df[f"{codigo}_res"] = df[codigo].apply(
                lambda v, u=umbral: _clasificar_un_cmi(v, u)
            )

    return df


# ---------------------------------------------------------------------------
# Pipeline completo
# ---------------------------------------------------------------------------

def limpiar(
    df: pd.DataFrame | None = None,
    umbral_nulos: float = 1.0,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Ejecuta el pipeline de limpieza completo y devuelve el DataFrame limpio.

    Parámetros
    ----------
    df           : DataFrame de entrada. Si None, lee el archivo principal.
    umbral_nulos : Fracción de nulos a partir de la cual se elimina una columna
                   (excluye columnas en _COLUMNAS_CLINICAS). Por defecto 1.0
                   (solo elimina columnas completamente vacías).
                   Ejemplo: 0.90 elimina columnas con ≥ 90 % de nulos.
    verbose      : Si True, imprime el progreso paso a paso.
    """
    if df is None:
        if verbose:
            print("Leyendo archivo principal...")
        df = leer_datos_principales()
        if verbose:
            print(f"  Cargado: {df.shape[0]} filas × {df.shape[1]} columnas\n")

    # El renombrado va ANTES de la eliminación por umbral para que las columnas
    # con sufijo .1 queden expuestas al filtro con su nombre definitivo.
    pasos_sin_args = [
        ("Eliminar filas corruptas (País != COL)",        eliminar_filas_corruptas),
        ("Eliminar primera serie de antibióticos vacía",  eliminar_primera_serie_antibioticos),
        ("Renombrar columnas con sufijo .1",              renombrar_columnas_duplicadas),
    ]

    for nombre, fn in pasos_sin_args:
        antes = df.shape
        df = fn(df)
        if verbose:
            print(f"  [{nombre}]")
            print(f"    {antes[0]} × {antes[1]}  →  {df.shape[0]} × {df.shape[1]}")

    # Eliminación por nulos (con umbral configurable y protección clínica)
    antes = df.shape
    df = eliminar_columnas_vacias(df, umbral_nulos=umbral_nulos)
    if verbose:
        etiqueta = (
            f"Eliminar columnas ≥ {umbral_nulos*100:.0f} % nulos"
            f" (protegiendo {len(_COLUMNAS_CLINICAS)} cols. clínicas)"
        )
        print(f"  [{etiqueta}]")
        print(f"    {antes[0]} × {antes[1]}  →  {df.shape[0]} × {df.shape[1]}")

    if verbose:
        print(f"\nLimpieza completa: {df.shape[0]} filas × {df.shape[1]} columnas")

    return df


# ---------------------------------------------------------------------------
# Ejecución directa
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Cambiar umbral_nulos para ajustar la agresividad de la limpieza.
    # Ejemplo: 0.90 elimina columnas con >= 90 % de nulos (salvo columnas clínicas).
    df = limpiar(umbral_nulos=1.0)

    print("\nAplicando clasificación R/S...")
    df_ab = leer_antibioticos()
    df = clasificar_resistencia(df, df_ab)

    cols_res = [c for c in df.columns if c.endswith("_res")]
    print(f"\nColumnas de resistencia ({len(cols_res)}): {cols_res}\n")

    print("Conteo R / S por antibiótico:")
    for col in cols_res:
        conteo = df[col].value_counts().to_dict()
        total = df[col].notna().sum()
        print(f"  {col:<12} {conteo}  ({total}/{len(df)} clasificados)")

    print(f"\nDataFrame final: {df.shape[0]} filas × {df.shape[1]} columnas")
