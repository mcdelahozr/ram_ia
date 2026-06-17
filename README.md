# RAM-IA — Análisis de Resistencia Antimicrobiana

Dashboard interactivo para el análisis exploratorio de datos (EDA) de resistencia bacteriana a antibióticos en pacientes adultos de Unidades de Cuidado Intensivo (UCI) en Colombia, en el marco del proyecto **GREBO 2025**.

---

## Descripción del proyecto

El estudio analiza el perfil de resistencia de microorganismos aislados en UCI adultas a partir de datos microbiológicos del año 2024–2025. El conjunto de datos principal (`BSD_Grebo_UCI_2025_adultos.xlsx`) contiene **2 341 aislamientos** con información demográfica, clínica y resultados de Concentración Mínima Inhibitoria (CMI) para más de 20 antibióticos.

### Objetivos

- Caracterizar la distribución de microorganismos en UCI adultas de Colombia.
- Calcular tasas de resistencia por antibiótico y por organismo.
- Identificar patrones temporales y por tipo de muestra clínica.
- Detectar microorganismos con marcadores de resistencia especial (BLEE, Carbapenemasa, MRSA).

---

## Estructura del proyecto

```
ram_ia/
│
├── app.py                          # Dashboard Streamlit (punto de entrada)
├── requirements.txt                # Dependencias Python
├── README.md
│
├── files/                          # Datos de entrada (no se suben al repo)
│   ├── BSD_Grebo_UCI_2025_adultos.xlsx   # Dataset principal
│   ├── Antibioticos.xlsx                 # Códigos y umbrales de resistencia
│   └── Resistencia.xlsx                  # CMI de referencia por organismo
│
└── src/
    ├── limpieza/
    │   └── limpieza.py             # Pipeline de limpieza y clasificación R/S
    ├── utilidades/
    │   └── importar_archivos.py    # Utilidades de lectura de archivos
    └── graficos/
        └── graficos                # (reservado para gráficos estáticos)
```

### Archivos de datos

| Archivo | Descripción |
|---|---|
| `BSD_Grebo_UCI_2025_adultos.xlsx` | Dataset principal: 2 341 aislamientos × 165 columnas (demografía, tipo de muestra, CMI por antibiótico) |
| `Antibioticos.xlsx` | 23 antibióticos con su código WHONET y umbral de resistencia (CMI ≥ X → Resistente) |
| `Resistencia.xlsx` | CMI de referencia por microorganismo (2 034 registros) |

---

## Módulo de limpieza (`src/limpieza/limpieza.py`)

El pipeline de limpieza ejecuta los siguientes pasos en orden:

| Paso | Descripción | Resultado |
|---|---|---|
| 1 | Lectura con `header=1` (fila 0 del Excel está vacía) | 2 346 filas × 165 cols |
| 2 | Elimina 4 filas corruptas (`País != 'COL'`) | 2 341 filas |
| 3 | Elimina primera serie de antibióticos (100 % nulos) | − 40 columnas |
| 4 | Renombra columnas con sufijo `.1` al nombre canónico | sin cambio de dimensión |
| 5 | Elimina columnas 100 % nulas o 100 % `False` | − 40 columnas → **85 cols** |
| 6 | Clasifica CMI como R / S usando umbrales de `Antibioticos.xlsx` | + 20 columnas `{ab}_res` |

### Funciones principales

```python
from src.limpieza.limpieza import (
    limpiar,               # Pipeline completo → DataFrame limpio
    clasificar_resistencia,# Agrega columnas {ab}_res (R/S/NaN)
    parsear_cmi,           # Convierte ">16" → (">", 16.0)
    leer_datos_principales,# Lee el Excel con header correcto
    leer_antibioticos,     # Lee Antibioticos.xlsx
    leer_resistencia,      # Lee Resistencia.xlsx
)

# Uso básico
df = limpiar()                              # limpieza estructural
df = clasificar_resistencia(df, leer_antibioticos())  # clasifica R/S
```

El parámetro `umbral_nulos` de `limpiar()` permite eliminar columnas con alta proporción de nulos (por defecto solo elimina columnas 100 % vacías):

```python
df = limpiar(umbral_nulos=0.90)  # elimina columnas con >= 90 % de nulos
```

---

## Clonar el repositorio

### Requisitos previos

- [Git](https://git-scm.com/) instalado
- Python 3.10 o superior

### Comandos Git básicos

```bash
# 1. Clonar el repositorio
git clone https://github.com/<usuario>/ram_ia.git
cd ram_ia

# 2. Ver el estado del repositorio
git status

# 3. Ver el historial de commits
git log --oneline

# 4. Crear una rama de trabajo
git checkout -b mi-rama-de-analisis

# 5. Agregar cambios y hacer commit
git add .
git commit -m "Descripción del cambio"

# 6. Subir cambios al repositorio remoto
git push origin mi-rama-de-analisis

# 7. Traer los últimos cambios del repositorio remoto
git pull origin main
```

> **Nota:** Los archivos de datos (`files/*.xlsx`) están excluidos del repositorio en `.gitignore`. Deben copiarse manualmente en la carpeta `files/` después de clonar.

---

## Instalación y ejecución

### 1. Crear un entorno virtual (recomendado)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Las dependencias son:

| Paquete | Uso |
|---|---|
| `pandas` | Manipulación de datos |
| `openpyxl` | Lectura de archivos Excel |
| `numpy` | Operaciones numéricas |
| `streamlit` | Dashboard interactivo |
| `plotly` | Gráficas interactivas |

### 3. Ejecutar el dashboard

```bash
streamlit run app.py
```

El dashboard se abrirá automáticamente en el navegador en `http://localhost:8501`.

### 4. Usar solo el módulo de limpieza (sin dashboard)

```bash
python src/limpieza/limpieza.py
```

Esto ejecuta el pipeline completo e imprime el resumen de resistencias en consola.

---

## Dashboard — Pestañas disponibles

| Pestaña | Contenido |
|---|---|
| 🏥 **Epidemiología** | KPIs generales, distribución por sexo, histograma de edad, pirámide edad-sexo, tipo de muestra, laboratorios |
| 🦠 **Microorganismos** | Top N organismos, clasificación Gram/Hongo, treemap jerárquico, heatmap organismo × muestra, distribución de edad por Gram |
| 💊 **Resistencia** | Tasas globales R/S por antibiótico, heatmap organismo × antibiótico, análisis por clase de antibiótico |
| 🔬 **Marcadores Clínicos** | BLEE, Carbapenemasa, Beta-lactamasa, D-test (resistencia inducible a clindamicina) |
| 📈 **Tendencias** | Aislamientos por mes, evolución de organismos principales, tasas de resistencia mensuales, carbapenémicos por organismo |
| 📋 **Datos** | Tabla filtrable con todos los aislamientos y descarga en CSV |

El **panel lateral** permite filtrar por laboratorio, microorganismo, tipo de muestra, clasificación Gram, sexo y rango de edad. Todos los filtros se aplican simultáneamente a todas las pestañas.

---

## Fuente de datos

- **GREBO** — Grupo para el Control de la Resistencia Bacteriana en Bogotá
- Período: diciembre 2024 – diciembre 2025
- Población: pacientes adultos (≥ 18 años) en UCI de instituciones participantes
- Codificación WHONET para microorganismos y antibióticos
