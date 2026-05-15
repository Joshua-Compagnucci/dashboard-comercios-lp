import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

# ======================================================
# CONFIG STREAMLIT
# ======================================================

st.set_page_config(
    page_title="Dashboard de análisis de sentimientos",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0F172A;
    color: white;
}
.block-container {
    padding-top: 1rem;
}
h1, h2, h3 {
    color: white;
}
.card {
    background-color: #111827;
    border-radius: 12px;
    padding: 14px;
    border: 1px solid #334155;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# CARGAR EXCEL DIRECTO
# ======================================================

df = pd.read_excel("comentarios_etiquetados_sentimiento.xlsx")
df.columns = df.columns.str.strip().str.lower()

df["comentario"] = df["comentario"].astype(str)

if "fecha" in df.columns:
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

df["sentimiento"] = (
    df["sentimiento"]
    .astype(str)
    .str.strip()
    .str.lower()
    .replace({
        "positivo": "Positivo",
        "pósitivo": "Positivo",
        "negativo": "Negativo",
        "neutral": "Neutral"
    })
)

# ======================================================
# DICCIONARIO DE TEMAS
# ======================================================

temas = {
    "economia_consumo": [
        "no consumo", "no hay consumo", "hay consumo", "consumo cambio",
        "el consumo cambio", "no llega a fin", "no llega fin", "fin de mes",
        "no hay plata", "plata en el bolsillo", "bolsillo", "no venden",
        "ventas", "vendes", "vender", "vendiendo",
        "comercios", "comercio", "comerciante", "comerciantes",
        "local", "locales", "cerraron", "cerró", "cierre", "crisis",
        "fundieron", "fundió", "miseria", "hambre", "no alcanza",
        "argentina es muy cara", "mercado libre", "internet",
        "todo internet", "forma de comprar", "no entro en un local",
        "dueños de los locales"
    ],
    "impuestos_tasas": [
        "impuestos municipales", "impuesto municipal", "tasas municipales",
        "180 tasas", "180% de las tasas", "suba del 180",
        "suba de tasas", "impuestos provinciales", "municipales provinciales",
        "impuestos nacionales", "te matan", "quieren cobrar",
        "cobrar fortuna", "estacionamiento medido", "vtv",
        "aumento de la vtv", "coparticipación", "tasas", "impuestos"
    ],
    "alquileres": [
        "bajen alquileres", "bajen los alquileres", "alquiler", "alquileres"
    ],
    "importaciones": [
        "importaciones", "apertura de importaciones", "abertura de importaciones",
        "china", "te lo hacen por menos", "habilitó la abertura"
    ],
    "inseguridad": [
        "inseguridad", "miedo", "miedo en la calle",
        "no quiera estar en la calle", "ya a las 19", "a las 19"
    ],
    "politica_ideologia": [
        "viva milei", "milei carajo", "libertad carajo", "milei",
        "presidente", "gobierno nacional", "kirchnerista",
        "pasquín kirchnerista", "0221 pasquín", "zurdo", "022zurdo",
        "cfk", "gobernador", "intendente", "municipalidad",
        "municipio", "culpa del presidente", "defendiendo al presidente",
        "la culpa es del presidente"
    ]
}

def detectar_categoria(texto, diccionario):
    texto = str(texto).lower()
    encontrados = []

    for categoria, frases in diccionario.items():
        for frase in frases:
            if frase in texto:
                encontrados.append(categoria)

    if encontrados:
        return ", ".join(sorted(set(encontrados)))

    return "otro"

df["tema"] = df["comentario"].apply(lambda x: detectar_categoria(x, temas))

# ======================================================
# PERFILES
# ======================================================

perfiles = {
    "comerciante": [
        "mi local", "mi comercio", "soy comerciante", "tengo un local",
        "vendo", "ventas", "clientes", "alquiler del local",
        "no vendo", "no vendemos", "comerciantes"
    ],
    "militante": [
        "viva milei", "milei carajo", "zurdo", "kuka", "kirchnerista",
        "peroncho", "cfk", "la casta", "libertad carajo",
        "pasquín", "defendiendo al presidente"
    ],
    "vecino_consumidor": [
        "no llego a fin", "no llega a fin", "no hay plata",
        "no consumo", "no compro", "caro", "carísimo",
        "bolsillo", "no alcanza"
    ],
    "anti_gestion": [
        "intendente", "municipio", "municipalidad", "gobernador",
        "presidente", "tasas", "impuestos", "vtv",
        "estacionamiento medido"
    ],
    "analitico": [
        "también", "además", "depende", "hay varios culpables",
        "no es solo", "incidencias", "cuestión", "cambio de consumo"
    ]
}

def detectar_perfil(texto):
    texto = str(texto).lower()
    encontrados = []

    for perfil, frases in perfiles.items():
        for frase in frases:
            if frase in texto:
                encontrados.append(perfil)

    if encontrados:
        return ", ".join(sorted(set(encontrados)))

    return "usuario_general"

df["perfil_usuario"] = df["comentario"].apply(detectar_perfil)

# ======================================================
# BUSCADOR GLOBAL SEMÁNTICO
# ======================================================

grupos_busqueda = {

    "milei": [
        "milei",
        "javier",
        "presidente",
        "gobierno nacional",
        "nacion",
        "nacional",
        "libertario",
        "libertarios"
    ],

    "kicillof": [
        "kicillof",
        "axel",
        "gobernador",
        "provincia",
        "provincial",
        "buenos aires",
        "vtv",
        "aumento de la vtv"
    ],

    "alak": [
        "alak",
        "intendente",
        "municipio",
        "municipal",
        "municipalidad",
        "ciudad",
        "tasas",
        "tasas municipales"
    ],

    "cristina": [
        "cristina",
        "cfk",
        "kirchner",
        "kirchnerismo"
    ],

    "macri": [
        "macri",
        "mauricio"
    ],

    "mercado libre": [
        "mercado libre",
        "internet",
        "online",
        "forma de comprar",
        "todo internet"
    ],

    "economia": [
        "crisis",
        "consumo",
        "no hay plata",
        "no alcanza",
        "comercios",
        "comerciante",
        "locales",
        "cierre"
    ],

    "alquileres": [
        "alquiler",
        "alquileres",
        "bajen alquileres",
        "bajen los alquileres"
    ]
}

# ======================================================
# CREAR MAPA INVERTIDO
# ======================================================

mapa_alias = {}

for grupo, aliases in grupos_busqueda.items():

    for alias in aliases:
        mapa_alias[alias.lower()] = aliases

# ======================================================
# INPUT
# ======================================================

busqueda = st.text_input(
    "Buscar palabra, tema, político o frase",
    placeholder="Ejemplo: kicillof, gobernador, milei, presidente..."
)

# ======================================================
# FILTRADO
# ======================================================

if busqueda:

    termino = busqueda.lower().strip()

    # Si pertenece a un grupo semántico
    if termino in mapa_alias:

        terminos_relacionados = mapa_alias[termino]

    else:

        terminos_relacionados = [termino]

    patron_busqueda = "|".join(
        [re.escape(t) for t in terminos_relacionados]
    )

    df_base = df[
        df["comentario"]
        .str.lower()
        .str.contains(
            patron_busqueda,
            regex=True,
            na=False
        )
    ].copy()

else:

    df_base = df.copy()

# ======================================================
# PREPARAR TEMAS FILTRADOS
# ======================================================

df_temas = df_base.copy()
df_temas["tema"] = df_temas["tema"].fillna("otro")
df_temas["tema"] = df_temas["tema"].str.split(", ")
df_temas = df_temas.explode("tema")

df_temas_sin_otro = df_temas[df_temas["tema"] != "otro"]

# ======================================================
# ESTILO MATPLOTLIB
# ======================================================

plt.rcParams["figure.facecolor"] = "#0F172A"
plt.rcParams["axes.facecolor"] = "#111827"
plt.rcParams["axes.edgecolor"] = "#334155"
plt.rcParams["axes.labelcolor"] = "white"
plt.rcParams["xtick.color"] = "#CBD5E1"
plt.rcParams["ytick.color"] = "#CBD5E1"
plt.rcParams["text.color"] = "white"
plt.rcParams["font.size"] = 11

colores = ["#8B5CF6", "#3B82F6", "#06B6D4", "#22C55E", "#F97316", "#EF4444"]

# ======================================================
# MÉTRICAS
# ======================================================

m1, m2, m3, m4 = st.columns(4)

m1.metric("Comentarios", len(df_base))
m2.metric("Negativos", int((df_base["sentimiento"] == "Negativo").sum()))
m3.metric("Neutrales", int((df_base["sentimiento"] == "Neutral").sum()))
m4.metric("Positivos", int((df_base["sentimiento"] == "Positivo").sum()))

# ======================================================
# FIGURA 1 - DONA SENTIMIENTOS + HALLAZGOS
# ======================================================

orden = ["Negativo", "Neutral", "Positivo"]
sentimientos = df_base["sentimiento"].value_counts().reindex(orden, fill_value=0)
sentimientos = sentimientos[sentimientos > 0]

total = sentimientos.sum()

colores_sent = {
    "Negativo": "#EF4444",
    "Neutral": "#64748B",
    "Positivo": "#22C55E"
}

fig_dona = plt.figure(figsize=(14, 7), facecolor="#0F172A")

ax1 = plt.subplot(1, 2, 1)
ax1.set_facecolor("#0F172A")

ax1.pie(
    sentimientos.values,
    labels=sentimientos.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=[colores_sent[x] for x in sentimientos.index],
    pctdistance=0.72,
    labeldistance=1.08,
    wedgeprops=dict(width=0.42, edgecolor="#0F172A"),
    textprops={"color": "white", "fontsize": 10}
)

ax1.set_title(
    f"Distribución de sentimiento\n{total} comentarios analizados",
    color="white",
    fontsize=18,
    fontweight="bold",
    loc="left"
)

ax2 = plt.subplot(1, 2, 2)
ax2.set_facecolor("#0F172A")
ax2.axis("off")

texto = """
HALLAZGOS PRINCIPALES

• Los comentarios positivos sostienen
  que el consumo migró hacia canales
  online como Mercado Libre.

• Los comentarios negativos apuntan
  principalmente a:
    - crisis económica
    - caída del consumo
    - impuestos y tasas
    - alquileres elevados

• Gran parte de las críticas mencionan
  tanto al Gobierno Nacional como
  a actores provinciales y municipales.

• El debate presenta un fuerte
  predominio de sentimiento negativo
  y polarización política.
"""

ax2.text(
    0,
    0.85,
    texto,
    fontsize=11,
    color="white",
    va="top"
)

plt.tight_layout()

# ======================================================
# FIGURA 2 - POLÍTICOS MÁS MENCIONADOS
# ======================================================

politicos_alias = {
    "Milei": [
        "milei", "javier", "presidente", "gobierno nacional",
        "nacion", "nacional", "libertario", "libertarios"
    ],
    "Cristina / CFK": [
        "cristina", "cfk", "kirchner", "kirchnerismo"
    ],
    "Kicillof": [
        "kicillof", "axel", "gobernador", "provincia",
        "provincial", "buenos aires", "vtv"
    ],
    "Alak": [
        "alak", "intendente", "municipio", "municipal",
        "ciudad", "tasas"
    ],
    "Macri": [
        "macri", "mauricio"
    ]
}

conteo_politicos = {}

comentarios = df_base["comentario"].astype(str).str.lower()

for politico, alias in politicos_alias.items():
    patron = "|".join(alias)
    cantidad = comentarios.str.contains(
        patron,
        regex=True,
        na=False
    ).sum()
    conteo_politicos[politico] = cantidad

conteo_politicos = pd.Series(conteo_politicos)
conteo = conteo_politicos.sort_values(ascending=False)

fig_politicos, ax = plt.subplots(figsize=(13, 8.5), facecolor="#0F172A")

ax.set_facecolor("#0F172A")
ax.axis("off")

ax.text(
    0.5, 0.94,
    "Políticos más mencionados",
    ha="center",
    va="center",
    fontsize=26,
    fontweight="bold",
    color="white"
)

ax.text(
    0.5, 0.90,
    "Menciones detectadas en comentarios de Instagram",
    ha="center",
    va="center",
    fontsize=12,
    color="#94A3B8"
)

y = 0.80

for i, (politico, valor) in enumerate(conteo.items(), start=1):

    ax.add_patch(
        plt.Rectangle(
            (0.13, y - 0.04),
            0.74,
            0.065,
            color="#1E293B"
        )
    )

    ax.text(
        0.17, y,
        f"{i}",
        ha="center",
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#A78BFA"
    )

    ax.text(
        0.24, y,
        politico,
        ha="left",
        va="center",
        fontsize=15,
        fontweight="bold",
        color="white"
    )

    ax.text(
        0.82, y,
        f"{valor} menciones",
        ha="right",
        va="center",
        fontsize=14,
        fontweight="bold",
        color="#38BDF8"
    )

    y -= 0.085

ax.add_patch(
    plt.Rectangle(
        (0.10, 0.05),
        0.80,
        0.25,
        color="#111827"
    )
)

ax.text(
    0.13,
    0.265,
    "Lectura general",
    fontsize=17,
    fontweight="bold",
    color="white",
    ha="left",
    va="center"
)

insights = [
    "Alak concentra la mayor parte de las menciones políticas.",
    "La conversación gira principalmente en torno a crisis económica, caída del consumo, impuestos y alquileres.",
    "Kicillof y actores municipales aparecen vinculados a tasas, VTV y presión fiscal.",
    "El tono general del debate es predominantemente negativo y altamente polarizado.",
    "Se observa una narrativa frecuente sobre el cambio del consumo hacia plataformas online."
]

y_text = 0.225

for item in insights:

    ax.text(
        0.13,
        y_text,
        "●",
        fontsize=12,
        color="#8B5CF6",
        ha="left",
        va="center"
    )

    ax.text(
        0.16,
        y_text,
        item,
        fontsize=11.5,
        color="#CBD5E1",
        ha="left",
        va="center"
    )

    y_text -= 0.04

plt.tight_layout()

fig_temas = plt.figure(figsize=(11, 6), facecolor="#0F172A")

if len(df_temas_sin_otro) > 0:

    temas_count = (
        df_temas_sin_otro["tema"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    # ======================================================
    # PORCENTAJES REALES
    # ======================================================

    total_menciones_temas = temas_count.sum()

    porcentajes = (
        temas_count / total_menciones_temas
    ) * 100

    # ======================================================
    # GRÁFICO
    # ======================================================

    plt.barh(
        temas_count.index,
        temas_count.values,
        color="#3B82F6"
    )

    # ======================================================
    # PORCENTAJES
    # ======================================================

    for i, porcentaje in enumerate(porcentajes.values):

        plt.text(
            temas_count.values[i] + 0.3,
            i,
            f"({porcentaje:.1f}%)",
            va="center",
            fontsize=11,
            color="white"
        )

    # ======================================================
    # TÍTULO
    # ======================================================

    plt.title(
        f"Temas más mencionados\nTotal de menciones temáticas: {total_menciones_temas}",
        fontsize=18,
        fontweight="bold",
        pad=15
    )

    plt.xlabel("Cantidad de menciones")

    plt.grid(axis="x", alpha=0.15)

else:

    plt.text(
        0.5,
        0.5,
        "No hay temas detectados",
        ha="center",
        va="center",
        fontsize=16
    )

    plt.axis("off")

plt.tight_layout()
# ======================================================
# FIGURA 4 - USUARIOS CON MÁS ME GUSTAS
# ======================================================

fig_usuarios, ax = plt.subplots(figsize=(11, 7), facecolor="#0F172A")
ax.set_facecolor("#111827")
ax.axis("off")

usuarios_likes = (
    df_base.groupby("usuario")["me_gustas"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

ax.text(
    0.5, 0.94,
    "Usuarios con más Me Gustas",
    ha="center",
    va="center",
    fontsize=22,
    fontweight="bold",
    color="white"
)

ax.text(
    0.5, 0.89,
    "Ranking de usuarios con mayor interacción acumulada",
    ha="center",
    va="center",
    fontsize=12,
    color="#94A3B8"
)

y = 0.80

for i, (usuario, likes) in enumerate(usuarios_likes.items(), start=1):

    ax.add_patch(
        plt.Rectangle(
            (0.08, y - 0.035),
            0.84,
            0.055,
            color="#1E293B",
            alpha=0.95
        )
    )

    ax.text(
        0.12, y,
        f"{i}",
        ha="center",
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#CBD5E1"
    )

    ax.text(
        0.18, y,
        f"@{usuario}",
        ha="left",
        va="center",
        fontsize=13,
        color="white"
    )

    ax.text(
        0.88, y,
        f"{likes} Me Gustas",
        ha="right",
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#A78BFA"
    )

    y -= 0.07

plt.tight_layout()

# ======================================================
# FIGURA 5 - EVOLUCIÓN DE TEMAS
# ======================================================

fig_evolucion = plt.figure(figsize=(14, 7), facecolor="#0F172A")

if len(df_temas_sin_otro) > 0:

    df_ordenado = df_temas_sin_otro.copy().reset_index(drop=True)

    # Bloques dinámicos según cantidad de comentarios filtrados
    if len(df_ordenado) <= 10:
        tam_bloque = 2
    elif len(df_ordenado) <= 30:
        tam_bloque = 5
    else:
        tam_bloque = 20

    df_ordenado["bloque"] = (df_ordenado.index // tam_bloque) + 1

    evolucion = (
        df_ordenado
        .groupby(["bloque", "tema"])
        .size()
        .reset_index(name="comentarios")
    )

    total_bloque = (
        evolucion
        .groupby("bloque")["comentarios"]
        .sum()
        .reset_index(name="total_bloque")
    )

    evolucion = evolucion.merge(total_bloque, on="bloque", how="left")

    evolucion["porcentaje"] = (
        evolucion["comentarios"] / evolucion["total_bloque"] * 100
    )

    evolucion_pivot = evolucion.pivot(
        index="bloque",
        columns="tema",
        values="porcentaje"
    ).fillna(0)

    temas_ordenados = (
        evolucion.groupby("tema")["comentarios"]
        .sum()
        .sort_values(ascending=False)
        .index
    )

    for i, tema in enumerate(temas_ordenados):

        plt.plot(
            evolucion_pivot.index,
            evolucion_pivot[tema],
            marker="o",
            linewidth=2.5,
            markersize=6,
            alpha=0.9,
            label=tema,
            color=colores[i % len(colores)]
        )

    plt.title(
        "Evolución de temas por bloques de comentarios",
        fontsize=18,
        fontweight="bold",
        pad=15
    )

    plt.xlabel(f"Bloques de {tam_bloque} comentarios")
    plt.ylabel("% de menciones del bloque")
    plt.grid(alpha=0.15)

    plt.legend(
        facecolor="#111827",
        edgecolor="#334155"
    )

    explicacion = f"""
El gráfico divide los comentarios en grupos de {tam_bloque} para poder ver cómo fue cambiando la conversación dentro de la búsqueda actual.

Si la búsqueda devuelve pocos comentarios, el tamaño del bloque se reduce automáticamente para que el gráfico siga mostrando variaciones.
"""

    plt.figtext(
        0.01,
        -0.12,
        explicacion,
        ha="left",
        fontsize=11,
        color="white",
        wrap=True
    )

else:

    plt.text(
        0.5,
        0.5,
        "No hay evolución de temas para esta búsqueda",
        ha="center",
        va="center",
        fontsize=16
    )

    plt.axis("off")

plt.tight_layout()
# ======================================================
# FIGURA 6 - PERFIL DE USUARIO
# ======================================================

df_perfiles = df_base.copy()
df_perfiles["perfil_usuario"] = df_perfiles["perfil_usuario"].str.split(", ")
df_perfiles = df_perfiles.explode("perfil_usuario")

perfil_count = df_perfiles["perfil_usuario"].value_counts().sort_values()

fig_perfiles = plt.figure(figsize=(10, 6), facecolor="#0F172A")

plt.barh(perfil_count.index, perfil_count.values, color="#8B5CF6")

plt.title("Perfil estimado de usuarios", fontsize=18, fontweight="bold", pad=15)
plt.xlabel("Cantidad de comentarios")
plt.grid(axis="x", alpha=0.15)
plt.tight_layout()

# ======================================================
# FIGURA 7 - NUBE DE PALABRAS
# ======================================================

stopwords = set([
    "de", "la", "el", "los", "las", "que", "y", "a", "en", "un", "una",
    "por", "con", "para", "del", "al", "se", "es", "no", "si", "lo",
    "como", "más", "pero", "ya", "eso", "este", "esta", "son", "su",
    "le", "te", "me", "mi", "tu", "hay", "porque", "q", "x", "los",
    "las", "dariodonadialp"
])

texto_wc = " ".join(df_base["comentario"].dropna().astype(str)).lower()
texto_wc = re.sub(r"@\w+", "", texto_wc)
texto_wc = re.sub(r"http\S+", "", texto_wc)

fig_nube, ax = plt.subplots(figsize=(13, 6), facecolor="#0F172A")

if texto_wc.strip():

    wc = WordCloud(
        width=1200,
        height=600,
        background_color="#0F172A",
        colormap="cool",
        stopwords=stopwords,
        collocations=False,
        max_words=120
    ).generate(texto_wc)

    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Nube de palabras", fontsize=18, fontweight="bold", pad=15)

else:
    ax.text(0.5, 0.5, "No hay palabras para mostrar", ha="center", va="center")
    ax.axis("off")

plt.tight_layout()

# ======================================================
# DASHBOARD
# ======================================================

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig_dona, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig_politicos, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns([1, 1])

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig_temas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig_usuarios, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col5, col6 = st.columns([1.4, 1])

with col5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig_evolucion, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig_perfiles, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col7, col8 = st.columns([1.2, 1])

with col7:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig_nube, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col8:
    st.subheader("Comentarios encontrados")

    columnas_mostrar = []

    for col in ["usuario", "comentario", "sentimiento", "tema", "perfil_usuario", "me_gustas", "fecha"]:
        if col in df_base.columns:
            columnas_mostrar.append(col)

    st.dataframe(
        df_base[columnas_mostrar],
        use_container_width=True,
        height=420
    )