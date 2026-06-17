"""
RAM-IA Dashboard — Análisis de Resistencia Antimicrobiana
GREBO | UCI Adultos Colombia 2024-2025
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from limpieza.limpieza import clasificar_resistencia, leer_antibioticos, limpiar

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="RAM-IA | UCI Adultos",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta de colores ─────────────────────────────────────────────────────────
COLOR_R = "#d62728"
COLOR_S = "#2ca02c"
COLOR_PRIMARY = "#1f77b4"
COLOR_GRAM = {
    "Gram-negativo": "#E76F51",
    "Gram-positivo": "#264653",
    "Hongo":         "#E9C46A",
    "Desconocido":   "#ADB5BD",
}

# ── Diccionarios de decodificación ────────────────────────────────────────────

MICROORGANISMOS = {
    "aba": "Acinetobacter baumannii",      "abx": "A. baumannii complex",
    "ac-": "Acinetobacter calcoaceticus",  "acb": "A. baumannii complex",
    "aeh": "Aeromonas hydrophila",         "alw": "Acinetobacter lwoffii",
    "aso": "Aeromonas sobria",             "aug": "Acinetobacter ursingii",
    "axy": "Achromobacter xylosoxidans",   "avv": "Advenella spp.",
    "bca": "Bacteroides spp.",             "bcs": "Bacteroides spp.",
    "bcx": "Bacteroides spp.",             "bfr": "Bacteroides fragilis",
    "bgl": "Bacteroides spp.",             "bpu": "Burkholderia pseudomallei",
    "bsb": "Bacillus spp.",               "bsl": "Bacillus spp.",
    "bvu": "Bacteroides vulgatus",
    "cac": "Clostridium spp.",            "cal": "Candida albicans",
    "cbk": "Candida krusei",              "cci": "Candida spp.",
    "cdi": "C. difficile",                "cdu": "C. difficile",
    "cfa": "Candida famata",              "cfr": "Candida famata",
    "cgl": "Candida glabrata",            "cgu": "Candida guilliermondii",
    "ci2": "Citrobacter spp.",            "cjk": "Candida krusei",
    "ckr": "Candida krusei",              "clo": "Clostridioides spp.",
    "clu": "Candida lusitaniae",          "cne": "Cryptococcus neoformans",
    "cor": "Corynebacterium spp.",        "cpa": "Candida parapsilosis",
    "cpe": "C. perfringens",             "cpp": "C. parapsilosis complex",
    "cra": "Candida ravautii",            "crs": "Candida spp.",
    "cso": "Candida sojae",              "cst": "Candida stellatoidea",
    "ctr": "Citrobacter freundii",        "ctt": "Candida tropicalis",
    "cyo": "Candida spp.",
    "eae": "Klebsiella aerogenes",        "eag": "Enterobacter agglomerans",
    "eas": "Enterobacter asburiae",       "eav": "Enterobacter spp.",
    "eca": "Enterobacter cancerogenus",   "ecl": "Enterobacter cloacae",
    "eco": "Escherichia coli",            "ecx": "E. cloacae complex",
    "edu": "Enterococcus durans",         "efa": "Enterococcus faecalis",
    "efm": "Enterococcus faecium",        "ega": "Enterococcus gallinarum",
    "egm": "Enterococcus spp.",           "ehm": "Enterococcus hirae",
    "en-": "Enterobacter spp.",           "enh": "Enterobacter hormaechei",
    "ent": "Enterococcus spp.",           "era": "Enterococcus raffinosus",
    "esa": "Enterococcus saccharolyticus",
    "fme": "Fusobacterium nucleatum",     "for": "Fusobacterium spp.",
    "gmo": "Granulicatella spp.",
    "haf": "Hafnia alvei",               "hin": "Haemophilus influenzae",
    "hpi": "Helicobacter pylori",
    "kas": "Klebsiella aerogenes",        "kl-": "Klebsiella spp.",
    "kor": "Klebsiella ornithinolytica",  "kox": "Klebsiella oxytoca",
    "koz": "Klebsiella ozaenae",          "kpl": "Klebsiella planticola",
    "kpn": "Klebsiella pneumoniae",       "kva": "Klebsiella variicola",
    "kvi": "Klebsiella variicola",
    "lla": "Lactobacillus spp.",          "lmo": "Listeria monocytogenes",
    "lut": "Luteimonas spp.",
    "mmo": "Morganella morganii",
    "nci": "Neisseria cinerea",
    "paa": "Pseudomonas alcaligenes",     "pae": "Pseudomonas aeruginosa",
    "pce": "Pseudomonas cedrina",         "pco": "Pseudomonas corrugata",
    "pes": "Pseudomonas spp.",            "pfl": "Pseudomonas fluorescens",
    "phs": "Pseudomonas spp.",            "pma": "Pseudomonas marginalis",
    "pmc": "Pseudomonas monteilii",       "pmg": "Pseudomonas migulae",
    "pmi": "Proteus mirabilis",           "pnd": "Pseudomonas spp.",
    "ppe": "Pseudomonas spp.",            "ppt": "Pseudomonas putida",
    "ppu": "Pseudomonas putida",          "pre": "Proteus rettgeri",
    "pro": "Proteus spp.",               "ps-": "Pseudomonas spp.",
    "psd": "Pseudomonas spp.",           "pse": "Pseudomonas spp.",
    "pst": "Pseudomonas stutzeri",        "pvu": "Proteus vulgaris",
    "rot": "Rothia spp.",
    "sal": "Salmonella spp.",            "san": "Staphylococcus simulans",
    "sap": "S. aureus (MRSA+)",          "sau": "Staphylococcus aureus",
    "sca": "Streptococcus agalactiae",   "scp": "Staphylococcus capitis",
    "sct": "Staphylococcus saprophyticus","sdy": "Shigella dysenteriae",
    "sep": "Staphylococcus epidermidis", "sfo": "Shigella spp.",
    "sgc": "Streptococcus spp.",         "sgu": "Streptococcus spp.",
    "sgy": "Streptococcus spp.",         "shl": "Staphylococcus haemolyticus",
    "sho": "Staphylococcus hominis",     "sin": "Staphylococcus spp.",
    "sit": "Staphylococcus spp.",        "sle": "Streptococcus spp.",
    "slq": "Staphylococcus lugdunensis", "slu": "Staphylococcus lugdunensis",
    "sma": "Stenotrophomonas maltophilia","smg": "Streptococcus mitis group",
    "smt": "Stenotrophomonas maltophilia","so1": "Staphylococcus spp.",
    "sol": "Staphylococcus haemolyticus","spa": "Staphylococcus pasteuri",
    "spn": "Streptococcus pneumoniae",   "spu": "Streptococcus spp.",
    "spy": "Streptococcus pyogenes",     "sqm": "Staphylococcus warneri",
    "ssa": "Staphylococcus saprophyticus","swa": "Staphylococcus warneri",
    "tas": "Tatumella spp.",             "tme": "Trabulsiella spp.",
    "vpa": "Vibrio parahaemolyticus",
}

_GRAM_NEG = frozenset({
    "aba","abx","ac-","acb","aeh","alw","aso","aug","axy","avv",
    "bca","bcs","bcx","bfr","bgl","bpu","bvu",
    "ci2","ctr","eae","eag","eas","eav","eca","ecl","eco","ecx",
    "en-","enh","fme","for","haf","hin","hpi",
    "kas","kl-","kor","kox","koz","kpl","kpn","kva","kvi",
    "lut","mmo","nci","paa","pae","pce","pco","pes","pfl","phs",
    "pma","pmc","pmg","pmi","pnd","ppe","ppt","ppu","pre","pro",
    "ps-","psd","pse","pst","pvu","rot","sal","sdy","sfo",
    "sma","smt","tas","tme","vpa",
})
_GRAM_POS = frozenset({
    "bsb","bsl","cac","cdi","cdu","clo","cpe","cor","edu",
    "efa","efm","ega","ehm","ent","era","esa",
    "gmo","lla","lmo","rot",
    "san","sap","sau","sca","scp","sct","sep","sgc","sgu","sgy",
    "shl","sho","sin","sit","sle","slq","slu","smg",
    "so1","sol","spa","spn","spu","spy","sqm","ssa","swa",
})
_HONGOS = frozenset({
    "cal","cbk","cci","cfa","cfr","cgl","cgu","cjk","ckr",
    "clu","cne","cpa","cpp","cra","crs","cso","cst","ctt","cyo",
})


def gram_de(codigo: str) -> str:
    c = str(codigo).lower().strip()
    if c in _HONGOS:   return "Hongo"
    if c in _GRAM_NEG: return "Gram-negativo"
    if c in _GRAM_POS: return "Gram-positivo"
    return "Desconocido"


TIPO_MUESTRA = {
    "sa":"Sangre","or":"Orina","tr":"Tráquea","tq":"Tráquea",
    "cm":"Catéter","ab":"Absceso","lb":"Lav. Broncoalveolar",
    "te":"Tejido","bi":"Bilis","es":"Esputo","ax":"Herida",
    "as":"Aspirado","se":"Secreción","ao":"Otro","oc":"Conjuntiva",
    "lp":"Líq. Pleural","lv":"Líquido","me":"LCR",
    "pe":"Líq. Peritoneal","pl":"Líq. Pleural","pn":"Pus",
    "ac":"Asp. catéter","ad":"Aspirado","at":"Asp. traqueal",
    "bo":"Boca","br":"Bronquio","bx":"Biopsia","bz":"Bronquio",
    "ca":"Catéter","cb":"Catéter","cc":"Catéter","ce":"Catéter",
    "cr":"Catéter","cz":"Catéter","da":"Drenaje","dr":"Drenaje",
    "ee":"Esputo","ef":"Esputo","ft":"Fístula","ga":"Gástrico",
    "gh":"Ganglio","ha":"Herida","he":"Herida","hi":"Hígado",
    "hs":"Herida","hu":"Hueso","ie":"Intestino","ig":"Intestino",
    "ll":"Líquido","lm":"Líquido","mm":"Muestra","mu":"Músculo",
    "na":"Nasal","oi":"Oído","oj":"Oído","pc":"Peritoneal",
    "pi":"Piel","pr":"Próstata","pu":"Pulmón","rd":"Recto",
    "re":"Recto","ri":"Recto","ul":"Úlcera","ur":"Urocultivo",
    "va":"Válvula","vb":"Vejiga",
}

ANTIBIOTICOS = {
    "AMP":"Ampicilina",       "SAM":"Amp-Sulbactam",    "TZP":"Pip-Tazobactam",
    "CZO":"Cefazolina",       "CXM":"Cefuroxima",       "CRO":"Ceftriaxona",
    "FOX":"Cefotaxima",       "CAZ":"Ceftazidima",      "FEP":"Cefepima",
    "ATM":"Aztreonam",        "ETP":"Ertapenem",        "IPM":"Imipenem",
    "MEM":"Meropenem",        "CIP":"Ciprofloxacino",   "LVX":"Levofloxacino",
    "AMK":"Amikacina",        "GEN":"Gentamicina",      "SXT":"TMP-SMX",
    "FOS":"Fosfomicina",      "NIT":"Nitrofurantoína",
}

GRUPOS_AB = {
    "Penicilinas":          ["AMP","SAM","TZP"],
    "Cefalosporinas / ATM": ["CZO","CXM","CRO","FOX","CAZ","FEP","ATM"],
    "Carbapenémicos":       ["ETP","IPM","MEM"],
    "Fluoroquinolonas":     ["CIP","LVX"],
    "Aminoglucósidos":      ["AMK","GEN"],
    "Otros":                ["SXT","FOS","NIT"],
}

# ── Carga y preprocesamiento (cacheado) ───────────────────────────────────────
@st.cache_data(show_spinner="Cargando y limpiando datos...")
def cargar_datos() -> pd.DataFrame:
    df = limpiar(verbose=False)
    df = clasificar_resistencia(df, leer_antibioticos())

    df["Organismo"] = (
        df["Microorganismo"]
        .map(MICROORGANISMOS)
        .fillna(df["Microorganismo"].str.upper())
    )
    df["Muestra"]   = df["Tipo de muestra"].map(TIPO_MUESTRA).fillna(df["Tipo de muestra"].str.upper())
    df["Gram"]      = df["Microorganismo"].fillna("").apply(gram_de)
    df["Edad"]      = pd.to_numeric(df["Edad"], errors="coerce")
    df["Año"]       = df["Fecha de muestra"].dt.year
    df["Año-Mes"]   = df["Fecha de muestra"].dt.to_period("M").astype(str)
    df["SexoLabel"] = df["Sexo"].map({"m": "Masculino", "f": "Femenino"})

    # Filtrar años con fechas evidentemente incorrectas
    df = df[df["Año"].between(2024, 2025)].copy()

    df["Grupo Edad"] = pd.cut(
        df["Edad"], bins=[17, 30, 45, 60, 75, 100],
        labels=["18-30", "31-45", "46-60", "61-75", ">75"], right=True,
    )
    return df


# ── Helpers ───────────────────────────────────────────────────────────────────
def tasa_r(series: pd.Series) -> float:
    s = series.dropna()
    return (s == "R").mean() * 100 if len(s) else np.nan


def resumen_resistencia(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ab, nombre in ANTIBIOTICOS.items():
        col = f"{ab}_res"
        if col not in df.columns:
            continue
        sub = df[col].dropna()
        n = len(sub)
        if n == 0:
            continue
        r = (sub == "R").sum()
        s = (sub == "S").sum()
        rows.append({
            "Antibiótico": nombre, "Código": ab,
            "Grupo": next((g for g, cs in GRUPOS_AB.items() if ab in cs), "Otros"),
            "N": n, "R": r, "S": s,
            "% R": round(r / n * 100, 1),
            "% S": round(s / n * 100, 1),
        })
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# CARGA
# ══════════════════════════════════════════════════════════════════════════════
df_full = cargar_datos()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🦠 RAM-IA")
    st.caption("GREBO · UCI Adultos Colombia · 2024-2025")
    st.divider()

    lab_opts   = sorted(df_full["Laboratorio"].dropna().unique())
    lab_sel    = st.multiselect("Laboratorio", lab_opts, placeholder="Todos")

    org_opts   = df_full["Organismo"].value_counts().head(40).index.tolist()
    org_sel    = st.multiselect("Microorganismo", org_opts, placeholder="Todos")

    mues_opts  = sorted(df_full["Muestra"].dropna().unique())
    mues_sel   = st.multiselect("Tipo de muestra", mues_opts, placeholder="Todos")

    gram_opts  = ["Todos"] + sorted(df_full["Gram"].unique())
    gram_sel   = st.selectbox("Clasificación Gram", gram_opts)

    sexo_sel   = st.selectbox("Sexo", ["Todos", "Masculino", "Femenino"])

    st.divider()
    edad_rng = st.slider(
        "Rango de edad", int(df_full["Edad"].min()), int(df_full["Edad"].max()),
        (int(df_full["Edad"].min()), int(df_full["Edad"].max())),
    )

# ── Aplicar filtros ───────────────────────────────────────────────────────────
df = df_full.copy()
if lab_sel:   df = df[df["Laboratorio"].isin(lab_sel)]
if org_sel:   df = df[df["Organismo"].isin(org_sel)]
if mues_sel:  df = df[df["Muestra"].isin(mues_sel)]
if gram_sel != "Todos": df = df[df["Gram"] == gram_sel]
if sexo_sel == "Masculino": df = df[df["Sexo"] == "m"]
if sexo_sel == "Femenino":  df = df[df["Sexo"] == "f"]
df = df[df["Edad"].between(edad_rng[0], edad_rng[1], inclusive="both") | df["Edad"].isna()]

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏥 Epidemiología",
    "🦠 Microorganismos",
    "💊 Resistencia",
    "🔬 Marcadores Clínicos",
    "📈 Tendencias",
    "📋 Datos",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 · Epidemiología
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Resumen epidemiológico — UCI Adultos")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Aislamientos",           f"{len(df):,}")
    c2.metric("Pacientes únicos",        f"{df['Número de identificación'].nunique():,}")
    c3.metric("Laboratorios",            df["Laboratorio"].nunique())
    c4.metric("Microorganismos distintos", df["Microorganismo"].nunique())
    c5.metric("Edad media (años)",       f"{df['Edad'].mean():.1f}")

    st.divider()
    r1c1, r1c2 = st.columns(2)

    # Sexo
    with r1c1:
        sc = df["SexoLabel"].value_counts().reset_index()
        sc.columns = ["Sexo", "N"]
        fig = px.pie(sc, values="N", names="Sexo", hole=0.45,
                     title="Distribución por sexo",
                     color="Sexo",
                     color_discrete_map={"Masculino":"#4477AA","Femenino":"#EE6677"})
        fig.update_traces(textinfo="percent+label+value")
        st.plotly_chart(fig, use_container_width=True)

    # Distribución de edad
    with r1c2:
        fig = px.histogram(df.dropna(subset=["Edad"]), x="Edad", nbins=25,
                           title="Distribución de edad",
                           color_discrete_sequence=[COLOR_PRIMARY],
                           labels={"Edad":"Edad (años)","count":"N aislamientos"})
        fig.update_layout(bargap=0.05)
        fig.add_vline(x=df["Edad"].median(), line_dash="dash",
                      annotation_text=f"Mediana: {df['Edad'].median():.0f}",
                      annotation_position="top right")
        st.plotly_chart(fig, use_container_width=True)

    r2c1, r2c2 = st.columns(2)

    # Tipo de muestra
    with r2c1:
        mc = df["Muestra"].value_counts().head(12).reset_index()
        mc.columns = ["Muestra","N"]
        fig = px.bar(mc.sort_values("N"), x="N", y="Muestra", orientation="h",
                     title="Tipo de muestra (top 12)",
                     color="N", color_continuous_scale="Blues",
                     labels={"N":"Aislamientos"})
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Laboratorio
    with r2c2:
        lc = df["Laboratorio"].value_counts().reset_index()
        lc.columns = ["Laboratorio","N"]
        fig = px.bar(lc, x="Laboratorio", y="N",
                     title="Aislamientos por laboratorio",
                     color="N", color_continuous_scale="Blues",
                     labels={"N":"Aislamientos"})
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Pirámide edad-sexo
    st.subheader("Pirámide de edad por sexo")
    pir = (
        df.dropna(subset=["Grupo Edad","SexoLabel"])
        .groupby(["Grupo Edad","SexoLabel"], observed=True)
        .size().reset_index(name="N")
    )
    pir_m = pir[pir["SexoLabel"] == "Masculino"]
    pir_f = pir[pir["SexoLabel"] == "Femenino"]
    grupos_orden = ["18-30","31-45","46-60","61-75",">75"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=pir_m["Grupo Edad"].astype(str), x=-pir_m["N"],
        orientation="h", name="Masculino", marker_color="#4477AA",
    ))
    fig.add_trace(go.Bar(
        y=pir_f["Grupo Edad"].astype(str), x=pir_f["N"],
        orientation="h", name="Femenino", marker_color="#EE6677",
    ))
    max_val = max(pir["N"].max(), 1)
    ticks   = list(range(0, max_val + 100, 100))
    fig.update_layout(
        barmode="relative", height=320,
        title="Pirámide de edad por sexo",
        yaxis=dict(categoryorder="array", categoryarray=grupos_orden),
        xaxis=dict(
            tickvals=[-v for v in ticks] + ticks,
            ticktext=[str(v) for v in ticks] + [str(v) for v in ticks],
            title="Número de aislamientos",
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 · Microorganismos
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Distribución de microorganismos")

    r1c1, r1c2 = st.columns([3, 2])

    with r1c1:
        n_top = st.slider("Organismos a mostrar", 5, 30, 15, key="sl_org")
        top_df = df["Organismo"].value_counts().head(n_top).reset_index()
        top_df.columns = ["Organismo","N"]
        fig = px.bar(top_df.sort_values("N"), x="N", y="Organismo",
                     orientation="h",
                     title=f"Top {n_top} microorganismos",
                     color="N", color_continuous_scale="Blues",
                     labels={"N":"Aislamientos"})
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        gc = df["Gram"].value_counts().reset_index()
        gc.columns = ["Gram","N"]
        fig = px.pie(gc, values="N", names="Gram", hole=0.42,
                     title="Clasificación Gram / Hongo",
                     color="Gram", color_discrete_map=COLOR_GRAM)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    # Treemap jerárquico
    st.subheader("Árbol de microorganismos")
    tm = (
        df[df["Gram"] != "Desconocido"]
        .groupby(["Gram","Organismo"])
        .size().reset_index(name="N")
    )
    fig = px.treemap(tm, path=["Gram","Organismo"], values="N",
                     color="Gram", color_discrete_map=COLOR_GRAM,
                     title="Distribución jerárquica (Gram → Organismo)")
    fig.update_traces(textinfo="label+value+percent parent")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Organismo por tipo de muestra (heatmap)
    st.subheader("Microorganismo × Tipo de muestra")
    n_org_hm = st.slider("Nº organismos", 5, 15, 10, key="sl_org_hm")
    n_mues_hm = st.slider("Nº tipos de muestra", 3, 12, 8, key="sl_mues_hm")
    top_org_l  = df["Organismo"].value_counts().head(n_org_hm).index
    top_mues_l = df["Muestra"].value_counts().head(n_mues_hm).index
    hm_df = (
        df[df["Organismo"].isin(top_org_l) & df["Muestra"].isin(top_mues_l)]
        .groupby(["Organismo","Muestra"]).size()
        .unstack(fill_value=0)
    )
    fig = px.imshow(hm_df, color_continuous_scale="Blues",
                    title="Frecuencia de aislamientos",
                    text_auto=True, aspect="auto",
                    labels={"color":"N aislamientos"})
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

    # Box plot edad por Gram
    st.subheader("Edad por clasificación Gram")
    fig = px.box(
        df.dropna(subset=["Edad","Gram"]),
        x="Gram", y="Edad", color="Gram",
        color_discrete_map=COLOR_GRAM,
        title="Distribución de edad por clasificación Gram",
        points="outliers",
    )
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 · Resistencia
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Tasas globales de resistencia")

    df_tasas = resumen_resistencia(df)

    if df_tasas.empty:
        st.warning("Sin datos suficientes para calcular tasas de resistencia.")
    else:
        # Barras apiladas R/S
        fig = px.bar(
            df_tasas.sort_values("% R"),
            y="Antibiótico", x=["% R","% S"],
            barmode="stack", orientation="h",
            title="Resistencia (R) y Sensibilidad (S) por antibiótico",
            color_discrete_map={"% R": COLOR_R, "% S": COLOR_S},
            labels={"value":"%","variable":""},
            hover_data=["N","Grupo"],
        )
        fig.update_layout(height=560, legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig, use_container_width=True)

        # Tabla
        st.dataframe(
            df_tasas[["Antibiótico","Código","Grupo","% R","% S","N"]]
            .sort_values("% R", ascending=False).reset_index(drop=True),
            use_container_width=True, hide_index=True,
        )

    st.divider()

    # Heatmap organismo × antibiótico
    st.subheader("Heatmap de resistencia: microorganismo × antibiótico")
    st.caption("Celdas en blanco = N < 5 aislamientos clasificados.")
    n_hm = st.slider("Nº organismos en el heatmap", 5, 20, 12, key="sl_hm")
    top_hm = df["Organismo"].value_counts().head(n_hm).index.tolist()
    df_sub = df[df["Organismo"].isin(top_hm)]

    hm_rows = []
    for ab, nombre in ANTIBIOTICOS.items():
        col = f"{ab}_res"
        if col not in df_sub.columns:
            continue
        for org, gdf in df_sub.groupby("Organismo"):
            s = gdf[col].dropna()
            hm_rows.append({
                "Organismo": org,
                "Antibiótico": nombre,
                "% R": round(tasa_r(s), 1) if len(s) >= 5 else np.nan,
                "N": len(s),
            })

    if hm_rows:
        piv = (
            pd.DataFrame(hm_rows)
            .pivot(index="Organismo", columns="Antibiótico", values="% R")
        )
        # Ordenar organismos por resistencia media descendente
        piv = piv.reindex(piv.mean(axis=1).sort_values(ascending=False).index)

        fig = px.imshow(
            piv,
            color_continuous_scale=["#2ca02c","#ffdd57","#d62728"],
            zmin=0, zmax=100,
            title="Tasa de resistencia (%) por organismo y antibiótico",
            aspect="auto",
            labels={"color":"% R"},
            text_auto=".0f",
        )
        fig.update_layout(height=520)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Resistencia por clase de antibiótico
    st.subheader("Resistencia por clase de antibiótico")
    grupo_sel = st.selectbox("Clase", list(GRUPOS_AB.keys()))
    abs_g = [ab for ab in GRUPOS_AB[grupo_sel] if f"{ab}_res" in df.columns]

    g_rows = []
    for ab in abs_g:
        s = df[f"{ab}_res"].dropna()
        if len(s):
            g_rows.append({
                "Antibiótico": ANTIBIOTICOS.get(ab, ab),
                "R": int((s=="R").sum()), "S": int((s=="S").sum()), "N": len(s),
            })
    if g_rows:
        df_g = pd.DataFrame(g_rows)
        fig = px.bar(df_g, x="Antibiótico", y=["R","S"], barmode="group",
                     title=f"R / S — {grupo_sel}",
                     color_discrete_map={"R": COLOR_R, "S": COLOR_S},
                     labels={"value":"Aislamientos","variable":""})
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 · Marcadores Clínicos
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Marcadores fenotípicos de resistencia especial")

    def grafico_marcador(col: str, titulo: str):
        if col not in df.columns:
            return
        s = df[col].dropna()
        if len(s) == 0:
            st.info(f"Sin datos de {titulo} en la selección actual.")
            return
        counts = s.value_counts().reset_index()
        counts.columns = ["Resultado","N"]
        pct_pos = (s == "+").mean() * 100
        st.metric(f"{titulo} — % positivos", f"{pct_pos:.1f}%", f"N={len(s)}")
        fig = px.bar(counts, x="Resultado", y="N",
                     color="Resultado",
                     color_discrete_map={"+": COLOR_R, "-": COLOR_S},
                     title=f"{titulo} (N total = {len(s)})",
                     labels={"N":"Aislamientos"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    with m1: grafico_marcador("BLEE",         "BLEE")
    with m2: grafico_marcador("Beta-lactamasa","Beta-lactamasa")
    with m3: grafico_marcador("Carbapenemase", "Carbapenemasa")

    st.divider()

    # Distribución por organismo
    for col_m, titulo in [
        ("BLEE","BLEE positiva"),
        ("Carbapenemase","Carbapenemasa positiva"),
        ("Beta-lactamasa","Beta-lactamasa positiva"),
    ]:
        if col_m not in df.columns:
            continue
        pos = df[df[col_m] == "+"]
        if len(pos) < 3:
            continue
        st.subheader(f"{titulo} — distribución por microorganismo")
        c1, c2 = st.columns([3, 2])
        with c1:
            org_c = pos["Organismo"].value_counts().head(12).reset_index()
            org_c.columns = ["Organismo","N"]
            fig = px.bar(org_c.sort_values("N"), x="N", y="Organismo",
                         orientation="h",
                         title=f"Organismos con {titulo}",
                         color_discrete_sequence=[COLOR_R])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            gram_c = pos["Gram"].value_counts().reset_index()
            gram_c.columns = ["Gram","N"]
            fig = px.pie(gram_c, values="N", names="Gram", hole=0.4,
                         title=f"Gram / Hongo — {titulo}",
                         color="Gram", color_discrete_map=COLOR_GRAM)
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

    # Resistencia inducible a clindamicina
    col_ric = "Resistencia inducible a la clindamicina"
    if col_ric in df.columns:
        s_ric = df[col_ric].dropna()
        if len(s_ric) >= 3:
            st.subheader("Resistencia inducible a la clindamicina (D-test)")
            rc = s_ric.value_counts().reset_index()
            rc.columns = ["Resultado","N"]
            fig = px.bar(rc, x="Resultado", y="N",
                         title=f"D-test (N={len(s_ric)})",
                         color_discrete_sequence=[COLOR_PRIMARY])
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 · Tendencias Temporales
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("Tendencias temporales")

    # Aislamientos por mes
    mensual = df.groupby("Año-Mes").size().reset_index(name="N")
    fig = px.line(mensual, x="Año-Mes", y="N", markers=True,
                  title="Aislamientos totales por mes",
                  labels={"Año-Mes":"Mes","N":"Aislamientos"})
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Evolución de organismos principales
    st.subheader("Evolución mensual — principales organismos")
    n_org_t = st.slider("Nº organismos", 3, 8, 5, key="sl_org_t")
    top_org_t = df["Organismo"].value_counts().head(n_org_t).index.tolist()
    org_mes = (
        df[df["Organismo"].isin(top_org_t)]
        .groupby(["Año-Mes","Organismo"]).size().reset_index(name="N")
    )
    if not org_mes.empty:
        fig = px.line(org_mes, x="Año-Mes", y="N", color="Organismo",
                      markers=True,
                      title=f"Evolución mensual — top {n_org_t} organismos",
                      labels={"Año-Mes":"Mes","N":"Aislamientos"})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Tendencia de resistencia (antibióticos clave)
    st.subheader("Tendencia de tasas de resistencia")
    abs_disp = [ab for ab in ANTIBIOTICOS if f"{ab}_res" in df.columns]
    abs_sel = st.multiselect(
        "Antibióticos a graficar",
        options=abs_disp,
        default=[a for a in ["CIP","MEM","IPM","CAZ","ETP"] if a in abs_disp],
        format_func=lambda x: f"{x} – {ANTIBIOTICOS[x]}",
    )

    trend_rows = []
    for mes, gdf in df.groupby("Año-Mes"):
        for ab in abs_sel:
            s = gdf[f"{ab}_res"].dropna()
            if len(s) >= 5:
                trend_rows.append({
                    "Mes": mes,
                    "Antibiótico": f"{ab} – {ANTIBIOTICOS[ab]}",
                    "% R": tasa_r(s),
                    "N": len(s),
                })

    if trend_rows:
        df_tr = pd.DataFrame(trend_rows)
        fig = px.line(df_tr, x="Mes", y="% R", color="Antibiótico",
                      markers=True,
                      title="Tasa de resistencia mensual (meses con N ≥ 5)",
                      labels={"% R":"% Resistente"})
        fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 100])
        fig.add_hline(y=50, line_dash="dash", line_color="gray",
                      annotation_text="50 %", annotation_position="right")
        st.plotly_chart(fig, use_container_width=True)
    elif abs_sel:
        st.info("Sin meses con N ≥ 5 aislamientos clasificados para los antibióticos seleccionados.")

    st.divider()

    # Resistencia a carbapenémicos por organismo
    st.subheader("Resistencia a carbapenémicos por organismo y mes")
    carb_abs = [ab for ab in ["IPM","MEM","ETP"] if f"{ab}_res" in df.columns]
    top3 = df["Organismo"].value_counts().head(5).index.tolist()
    org_carb_sel = st.multiselect("Organismos", top3, default=top3[:3], key="org_carb")

    carb_rows = []
    for org in org_carb_sel:
        df_o = df[df["Organismo"] == org]
        for mes, gdf in df_o.groupby("Año-Mes"):
            for ab in carb_abs:
                s = gdf[f"{ab}_res"].dropna()
                if len(s) >= 3:
                    carb_rows.append({
                        "Mes": mes, "Organismo": org,
                        "Antibiótico": ANTIBIOTICOS[ab],
                        "% R": tasa_r(s), "N": len(s),
                    })

    if carb_rows:
        df_carb = pd.DataFrame(carb_rows)
        fig = px.line(df_carb, x="Mes", y="% R",
                      color="Organismo", line_dash="Antibiótico",
                      markers=True,
                      title="Resistencia a carbapenémicos — organismos seleccionados",
                      labels={"% R":"% Resistente"})
        fig.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    elif org_carb_sel:
        st.info("Sin meses con N ≥ 3 aislamientos clasificados para la selección.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 · Datos
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.subheader(f"Datos filtrados — {len(df):,} aislamientos")

    cols_show = [
        "Número de identificación","Apellido","Nombre","SexoLabel","Edad",
        "Grupo Edad","Fecha de muestra","Laboratorio","Institución","Servicio",
        "Organismo","Gram","Muestra",
        "BLEE","Carbapenemase","Beta-lactamasa","MRSA",
    ] + [f"{ab}_res" for ab in ANTIBIOTICOS if f"{ab}_res" in df.columns]

    cols_show = [c for c in cols_show if c in df.columns]

    df_show = df[cols_show].rename(columns={
        "SexoLabel":"Sexo",
        **{f"{ab}_res": f"{ab} (R/S)" for ab in ANTIBIOTICOS},
    }).reset_index(drop=True)

    st.dataframe(df_show, use_container_width=True, height=480)

    csv = df_show.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar CSV filtrado",
        data=csv,
        file_name="ram_ia_datos.csv",
        mime="text/csv",
    )
