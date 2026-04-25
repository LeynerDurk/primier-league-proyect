# =============================================================================
#  PREMIER LEAGUE ANALYTICS DASHBOARD
#  Versión 2.0 · 1993–2025 · Dashboard interactivo en español
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================================================
#  CONFIGURACIÓN INICIAL
# =============================================================================

st.set_page_config(
    page_title="Premier League Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
#  ESTILOS CSS
# =============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"]       { font-family: 'Inter', sans-serif; }
    .stApp                           { background-color: #0d1117; }

    /* Sidebar */
    [data-testid="stSidebar"]        { background: linear-gradient(180deg,#161b22 0%,#0d1117 100%);
                                       border-right: 1px solid #30363d; }

    /* Tarjetas métricas */
    [data-testid="metric-container"] { background:#161b22; border:1px solid #30363d;
                                       border-radius:12px; padding:16px 20px; }
    [data-testid="metric-container"] label
                                     { color:#8b949e !important; font-size:0.75rem !important;
                                       text-transform:uppercase; letter-spacing:0.08em; }
    [data-testid="metric-container"] [data-testid="stMetricValue"]
                                     { color:#f0f6fc !important; font-size:1.8rem !important; font-weight:700; }

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"]{ background:#161b22; border-radius:8px; }
    .stTabs [data-baseweb="tab"]     { color:#8b949e; font-weight:500; }
    .stTabs [aria-selected="true"]   { color:#38d9f5 !important; }

    /* Textos generales */
    h1  { color:#f0f6fc !important; font-weight:700; }
    h2,h3 { color:#c9d1d9 !important; }
    hr  { border-color:#30363d; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
#  CONSTANTES DE DISEÑO
# =============================================================================

FONDO_GRAFICA  = "#161b22"
FONDO_PAPEL    = "#161b22"
COLOR_GRILLA   = "#21262d"
ACENTO         = "#38d9f5"
PALETA = [
    "#38d9f5", "#7c3aed", "#f59e0b", "#10b981",
    "#ef4444", "#3b82f6", "#ec4899", "#14b8a6",
    "#f97316", "#6366f1",
]

# =============================================================================
#  FUNCIÓN UTILITARIA: aplicar estilo base a cualquier figura
# =============================================================================

def estilizar(fig, titulo="", alto=420):
    """Aplica el tema oscuro y fuentes consistentes a una figura Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=FONDO_PAPEL,
        plot_bgcolor=FONDO_GRAFICA,
        height=alto,
        title=dict(text=titulo, font=dict(size=15, color="#c9d1d9"), x=0.01, xanchor="left"),
        font=dict(family="Inter", color="#8b949e"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#30363d", borderwidth=1),
        xaxis=dict(gridcolor=COLOR_GRILLA, linecolor="#30363d", tickfont=dict(size=11)),
        yaxis=dict(gridcolor=COLOR_GRILLA, linecolor="#30363d", tickfont=dict(size=11)),
    )
    return fig


def mostrar(fig):
    """Renderiza una figura sin barra de herramientas."""
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# =============================================================================
#  CARGA Y PREPARACIÓN DE DATOS
# =============================================================================

@st.cache_data
def cargar_datos():
    """Carga el CSV y agrega columnas calculadas."""
    df = pd.read_csv("PremierLeague.csv")

    # Goles totales
    df["TotalGoles"] = df["FullTimeHomeTeamGoals"] + df["FullTimeAwayTeamGoals"]

    # Goles de medio tiempo
    df["GTMedio"] = df["HalfTimeHomeTeamGoals"] + df["HalfTimeAwayTeamGoals"]

    # Resultado al medio tiempo calculado desde goles
    df["ResultadoMT"] = "E"
    df.loc[df["HalfTimeHomeTeamGoals"] > df["HalfTimeAwayTeamGoals"], "ResultadoMT"] = "L"
    df.loc[df["HalfTimeHomeTeamGoals"] < df["HalfTimeAwayTeamGoals"], "ResultadoMT"] = "V"

    # Etiqueta legible del resultado final
    mapa_resultado = {"H": "Local gana", "D": "Empate", "A": "Visitante gana"}
    df["ResultadoLabel"] = df["FullTimeResult"].map(mapa_resultado)

    # Fecha
    df["Fecha"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)

    return df


df = cargar_datos()

TODAS_TEMPORADAS = sorted(df["Season"].unique())
TODOS_EQUIPOS    = sorted(set(df["HomeTeam"].tolist() + df["AwayTeam"].tolist()))

# =============================================================================
#  SIDEBAR — FILTROS
# =============================================================================

with st.sidebar:
    st.markdown("## ⚽ Premier League")
    st.markdown("### Filtros de Análisis")
    st.markdown("---")

    # --- Temporadas ---
    st.markdown("**🗓 Temporadas**")
    temporadas_sel = st.multiselect(
        "Temporadas",
        options=TODAS_TEMPORADAS,
        default=TODAS_TEMPORADAS[-10:],
        label_visibility="collapsed",
    )
    if not temporadas_sel:
        temporadas_sel = TODAS_TEMPORADAS

    # --- Equipos ---
    st.markdown("**🏟 Equipos**")
    equipos_sel = st.multiselect(
        "Equipos",
        options=TODOS_EQUIPOS,
        default=[],
        placeholder="Todos los equipos",
        label_visibility="collapsed",
    )

    # --- Rango de goles ---
    st.markdown("**⚽ Goles por partido**")
    min_g = int(df["TotalGoles"].min())
    max_g = int(df["TotalGoles"].max())
    rango_goles = st.slider("Goles totales", min_g, max_g, (min_g, max_g))

    # --- Resultado ---
    st.markdown("**📊 Resultado del partido**")
    opciones_resultado = ["H (Local gana)", "D (Empate)", "A (Visitante gana)"]
    resultados_sel = st.multiselect(
        "Resultado",
        options=opciones_resultado,
        default=opciones_resultado,
        label_visibility="collapsed",
    )
    mapa_res = {"H (Local gana)": "H", "D (Empate)": "D", "A (Visitante gana)": "A"}
    codigos_res = [mapa_res[r] for r in resultados_sel] if resultados_sel else ["H", "D", "A"]

    st.markdown("---")
    st.caption("📊 Datos: 1993–2025 · 12,160 partidos")

# =============================================================================
#  APLICAR FILTROS
# =============================================================================

dff = df[
    df["Season"].isin(temporadas_sel) &
    df["TotalGoles"].between(*rango_goles) &
    df["FullTimeResult"].isin(codigos_res)
].copy()

if equipos_sel:
    dff = dff[dff["HomeTeam"].isin(equipos_sel) | dff["AwayTeam"].isin(equipos_sel)]

# =============================================================================
#  ENCABEZADO PRINCIPAL
# =============================================================================

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
  <span style="font-size:2.4rem">⚽</span>
  <div>
    <h1 style="margin:0;font-size:2rem">Premier League Analytics</h1>
    <span style="color:#8b949e;font-size:0.9rem">
      Dashboard de análisis estadístico · 1993–2025
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
#  KPIs GLOBALES
# =============================================================================

victorias_local    = len(dff[dff["FullTimeResult"] == "H"])
empates            = len(dff[dff["FullTimeResult"] == "D"])
victorias_visita   = len(dff[dff["FullTimeResult"] == "A"])
promedio_goles     = dff["TotalGoles"].mean() if len(dff) else 0
total_goles        = dff["TotalGoles"].sum()
pct_local          = victorias_local / len(dff) * 100 if len(dff) else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("⚽ Partidos",              f"{len(dff):,}")
c2.metric("🏠 Victorias Local",       f"{victorias_local:,}",  f"{pct_local:.1f}%")
c3.metric("🤝 Empates",               f"{empates:,}")
c4.metric("✈️ Victorias Visitante",   f"{victorias_visita:,}")
c5.metric("⚽ Total Goles",           f"{int(total_goles):,}")
c6.metric("📊 Prom. Goles/Partido",   f"{promedio_goles:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
#  PESTAÑAS PRINCIPALES
# =============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅  Resultados & Tendencias",
    "⚽  Goles",
    "🏆  Equipos",
    "🎯  Eficiencia",
    "⏱  Medio Tiempo",
])


# ─────────────────────────────────────────────────────────────────────────────
#  PESTAÑA 1 — RESULTADOS & TENDENCIAS
# ─────────────────────────────────────────────────────────────────────────────

with tab1:

    # --- Gráfica 1: Resultados por temporada (barras apiladas) ---
    resultados_temporada = (
        dff.groupby(["Season", "ResultadoLabel"])
        .size()
        .reset_index(name="Partidos")
    )
    resultados_temporada["Temporada"] = resultados_temporada["Season"].str[-4:]

    fig1 = px.bar(
        resultados_temporada,
        x="Temporada", y="Partidos", color="ResultadoLabel",
        color_discrete_map={
            "Local gana":      ACENTO,
            "Empate":          "#f59e0b",
            "Visitante gana":  "#7c3aed",
        },
        barmode="stack",
        custom_data=["Season", "ResultadoLabel", "Partidos"],
    )
    fig1.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[1]}: <b>%{customdata[2]} partidos</b>"
            "<extra></extra>"
        )
    )
    fig1 = estilizar(fig1, "📅 Distribución de Resultados por Temporada", alto=400)
    fig1.update_layout(xaxis_title="Temporada", yaxis_title="Nº Partidos")
    mostrar(fig1)

    col_a, col_b = st.columns(2)

    with col_a:
        # --- Gráfica 2: % Victorias local por temporada (línea) ---
        ventaja_local = (
            dff.groupby("Season")["FullTimeResult"]
            .apply(lambda x: round((x == "H").mean() * 100, 1))
            .reset_index(name="PctLocal")
        )
        ventaja_local["Temporada"] = ventaja_local["Season"].str[-4:]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=ventaja_local["Temporada"],
            y=ventaja_local["PctLocal"],
            mode="lines+markers",
            name="% Local gana",
            line=dict(color=ACENTO, width=3),
            marker=dict(size=7),
            customdata=ventaja_local[["Season", "PctLocal"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Victorias local: <b>%{customdata[1]:.1f}%</b>"
                "<extra></extra>"
            ),
        ))
        fig2.add_hline(
            y=ventaja_local["PctLocal"].mean(),
            line_dash="dot", line_color="#f59e0b", line_width=1.5,
            annotation_text=f"Promedio histórico: {ventaja_local['PctLocal'].mean():.1f}%",
            annotation_font_color="#f59e0b",
        )
        fig2 = estilizar(fig2, "🏠 % Victorias Local por Temporada", alto=380)
        fig2.update_layout(xaxis_title="Temporada", yaxis_title="% Victorias local")
        mostrar(fig2)

    with col_b:
        # --- Gráfica 3: Torta de resultados globales ---
        conteo_resultados = dff["ResultadoLabel"].value_counts().reset_index()
        conteo_resultados.columns = ["Resultado", "Partidos"]

        fig3 = go.Figure(go.Pie(
            labels=conteo_resultados["Resultado"],
            values=conteo_resultados["Partidos"],
            hole=0.55,
            marker=dict(colors=[ACENTO, "#7c3aed", "#f59e0b"],
                        line=dict(color=FONDO_GRAFICA, width=3)),
            customdata=conteo_resultados[["Resultado", "Partidos"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Partidos: <b>%{customdata[1]:,}</b><br>"
                "Porcentaje: <b>%{percent}</b>"
                "<extra></extra>"
            ),
            textfont=dict(size=13),
        ))
        fig3 = estilizar(fig3, "🥧 Proporción Global de Resultados", alto=380)
        fig3.update_layout(legend=dict(orientation="h", y=-0.1))
        mostrar(fig3)


# ─────────────────────────────────────────────────────────────────────────────
#  PESTAÑA 2 — GOLES
# ─────────────────────────────────────────────────────────────────────────────

with tab2:

    col_a, col_b = st.columns(2)

    with col_a:
        # --- Gráfica 4: Promedio de goles por temporada ---
        goles_temporada = (
            dff.groupby("Season")
            .agg(
                PromTotal=("TotalGoles", "mean"),
                PromLocal=("FullTimeHomeTeamGoals", "mean"),
                PromVisita=("FullTimeAwayTeamGoals", "mean"),
                Partidos=("TotalGoles", "count"),
            )
            .reset_index()
        )
        goles_temporada["Temporada"] = goles_temporada["Season"].str[-4:]

        fig4 = go.Figure()
        for col, nombre, color, ancho in [
            ("PromTotal",  "Total",      ACENTO,    3),
            ("PromLocal",  "Local",      "#10b981", 2),
            ("PromVisita", "Visitante",  "#f59e0b", 2),
        ]:
            fig4.add_trace(go.Scatter(
                x=goles_temporada["Temporada"],
                y=goles_temporada[col],
                name=nombre,
                mode="lines+markers",
                line=dict(color=color, width=ancho),
                marker=dict(size=6),
                customdata=goles_temporada[["Season", "PromTotal", "PromLocal", "PromVisita", "Partidos"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Total: <b>%{customdata[1]:.2f}</b><br>"
                    "Local: <b>%{customdata[2]:.2f}</b> · "
                    "Visitante: <b>%{customdata[3]:.2f}</b><br>"
                    "Partidos: %{customdata[4]}"
                    "<extra></extra>"
                ),
            ))
        fig4 = estilizar(fig4, "📈 Evolución de Goles Promedio por Temporada", alto=380)
        fig4.update_layout(xaxis_title="Temporada", yaxis_title="Goles promedio")
        mostrar(fig4)

    with col_b:
        # --- Gráfica 5: Histograma de distribución de goles totales ---
        conteo_goles = dff["TotalGoles"].value_counts().sort_index().reset_index()
        conteo_goles.columns = ["Goles", "Partidos"]
        conteo_goles["Pct"] = (conteo_goles["Partidos"] / len(dff) * 100).round(1)

        fig5 = go.Figure(go.Bar(
            x=conteo_goles["Goles"],
            y=conteo_goles["Partidos"],
            marker=dict(
                color=conteo_goles["Goles"],
                colorscale=[[0, "#1a1f2e"], [0.4, ACENTO], [1, "#f0f6fc"]],
                line=dict(color=FONDO_GRAFICA, width=1),
            ),
            customdata=conteo_goles[["Goles", "Partidos", "Pct"]].values,
            hovertemplate=(
                "<b>%{customdata[0]} goles en el partido</b><br>"
                "Partidos: <b>%{customdata[1]:,}</b><br>"
                "Del total: <b>%{customdata[2]}%</b>"
                "<extra></extra>"
            ),
        ))
        fig5 = estilizar(fig5, "📊 Distribución de Goles por Partido", alto=380)
        fig5.update_layout(xaxis_title="Goles en el partido", yaxis_title="Nº Partidos",
                           xaxis=dict(tickmode="linear", dtick=1))
        mostrar(fig5)

    # --- Gráfica 6: Violin local vs visitante ---
    col_c, col_d = st.columns(2)

    with col_c:
        df_violin = pd.DataFrame({
            "Goles": (list(dff["FullTimeHomeTeamGoals"]) +
                      list(dff["FullTimeAwayTeamGoals"])),
            "Tipo":  (["Local"] * len(dff) + ["Visitante"] * len(dff)),
        })

        fig6 = go.Figure()
        for tipo, color in [("Local", ACENTO), ("Visitante", "#7c3aed")]:
            sub = df_violin[df_violin["Tipo"] == tipo]
            fig6.add_trace(go.Violin(
                x=sub["Tipo"], y=sub["Goles"],
                name=tipo, fillcolor=color,
                line_color=color, opacity=0.7,
                box_visible=True, meanline_visible=True,
                points="outliers",
                hoverinfo="name+y",
            ))
        fig6 = estilizar(fig6, "🎻 Distribución de Goles: Local vs Visitante", alto=380)
        fig6.update_layout(yaxis_title="Goles por partido", xaxis_title="",
                           violingap=0.3)
        fig6.update_xaxes(gridcolor=COLOR_GRILLA)
        fig6.update_yaxes(gridcolor=COLOR_GRILLA)
        mostrar(fig6)

    with col_d:
        # --- Gráfica 7: Heatmap goles por temporada y jornada ---
        pivot = (
            dff.groupby(["Season", "MatchWeek"])["TotalGoles"]
            .mean()
            .reset_index()
            .pivot(index="Season", columns="MatchWeek", values="TotalGoles")
        )
        pivot = pivot.reindex(sorted(pivot.index))

        fig7 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"J{c}" for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[
                [0.0, "#0d1117"], [0.3, "#1a3a5c"],
                [0.6, "#1d6fa4"], [0.8, ACENTO], [1.0, "#f0f6fc"],
            ],
            hoverongaps=False,
            hovertemplate=(
                "<b>%{y}</b> · Jornada %{x}<br>"
                "Goles promedio: <b>%{z:.2f}</b>"
                "<extra></extra>"
            ),
            colorbar=dict(
                title=dict(text="Goles<br>prom.", font=dict(color="#8b949e", size=11)),
                tickfont=dict(color="#8b949e"),
                thickness=12,
            ),
        ))
        fig7 = estilizar(fig7, "🔥 Heatmap: Goles por Temporada y Jornada", alto=380)
        fig7.update_layout(
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(tickfont=dict(size=9)),
        )
        mostrar(fig7)


# ─────────────────────────────────────────────────────────────────────────────
#  PESTAÑA 3 — EQUIPOS
# ─────────────────────────────────────────────────────────────────────────────

with tab3:

    # Construir tabla de estadísticas por equipo
    todos_equipos = pd.concat([dff["HomeTeam"], dff["AwayTeam"]]).unique()

    vl = dff[dff["FullTimeResult"] == "H"].groupby("HomeTeam").size().rename("VL")
    vv = dff[dff["FullTimeResult"] == "A"].groupby("AwayTeam").size().rename("VV")
    el = dff[dff["FullTimeResult"] == "D"].groupby("HomeTeam").size().rename("EL")
    ev = dff[dff["FullTimeResult"] == "D"].groupby("AwayTeam").size().rename("EV")
    gl = dff.groupby("HomeTeam")["FullTimeHomeTeamGoals"].sum().rename("GL")
    gv = dff.groupby("AwayTeam")["FullTimeAwayTeamGoals"].sum().rename("GV")
    gcl = dff.groupby("HomeTeam")["FullTimeAwayTeamGoals"].sum().rename("GCL")
    gcv = dff.groupby("AwayTeam")["FullTimeHomeTeamGoals"].sum().rename("GCV")

    est = pd.DataFrame(index=todos_equipos)
    est = est.join([vl, vv, el, ev, gl, gv, gcl, gcv]).fillna(0)
    est["Victorias"] = est["VL"] + est["VV"]
    est["Empates"]   = est["EL"] + est["EV"]
    est["GF"]        = est["GL"] + est["GV"]
    est["GC"]        = est["GCL"] + est["GCV"]
    est["Derrotas"]  = (
        dff.groupby("HomeTeam").size().reindex(est.index).fillna(0) +
        dff.groupby("AwayTeam").size().reindex(est.index).fillna(0)
        - est["Victorias"] - est["Empates"]
    )
    est["Partidos"]  = est["Victorias"] + est["Empates"] + est["Derrotas"]
    est["PctVict"]   = (est["Victorias"] / est["Partidos"] * 100).round(1)
    est["DifGoles"]  = est["GF"] - est["GC"]
    est.index.name = "Equipo"
    est = est.reset_index()

    col_a, col_b = st.columns(2)

    with col_a:
        # --- Gráfica 8: Top 15 victorias (barras horizontales apiladas) ---
        top15 = est.nlargest(15, "Victorias").sort_values("Victorias")

        fig8 = go.Figure()
        for col, nombre, color in [
            ("VL", "Victoria Local",     ACENTO),
            ("VV", "Victoria Visitante", "#7c3aed"),
        ]:
            fig8.add_trace(go.Bar(
                y=top15["Equipo"], x=top15[col],
                name=nombre, orientation="h",
                marker_color=color,
                customdata=top15[["Equipo", "VL", "VV", "Victorias", "GF", "PctVict"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "🏠 Local: <b>%{customdata[1]:.0f}</b>  "
                    "✈️ Visita: <b>%{customdata[2]:.0f}</b><br>"
                    "🏆 Total victorias: <b>%{customdata[3]:.0f}</b><br>"
                    "⚽ Goles marcados: <b>%{customdata[4]:.0f}</b><br>"
                    "Win rate: <b>%{customdata[5]:.1f}%</b>"
                    "<extra></extra>"
                ),
            ))
        fig8.update_layout(barmode="stack")
        fig8 = estilizar(fig8, "🏆 Top 15 Equipos por Victorias Totales", alto=460)
        fig8.update_layout(
            xaxis_title="Victorias",
            legend=dict(orientation="h", y=1.05),
        )
        mostrar(fig8)

    with col_b:
        # --- Gráfica 9: Win rate de todos los equipos (con mínimo de partidos) ---
        min_partidos = 100
        est_filtrado = est[est["Partidos"] >= min_partidos].sort_values("PctVict", ascending=True)

        colores_barra = [
            "#ef4444" if v < 30 else "#f59e0b" if v < 45 else "#10b981"
            for v in est_filtrado["PctVict"]
        ]

        fig9 = go.Figure(go.Bar(
            y=est_filtrado["Equipo"],
            x=est_filtrado["PctVict"],
            orientation="h",
            marker=dict(color=colores_barra, line=dict(color=FONDO_GRAFICA, width=0.5)),
            customdata=est_filtrado[["Equipo", "Partidos", "Victorias", "PctVict", "DifGoles"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Partidos jugados: <b>%{customdata[1]:.0f}</b><br>"
                "Victorias: <b>%{customdata[2]:.0f}</b><br>"
                "Win rate: <b>%{customdata[3]:.1f}%</b><br>"
                "Diferencia de goles: <b>%{customdata[4]:+.0f}</b>"
                "<extra></extra>"
            ),
        ))
        fig9.add_vline(x=45.8, line_dash="dot", line_color="#f59e0b",
                       annotation_text="Media PL 45.8%",
                       annotation_font_color="#f59e0b")
        fig9 = estilizar(fig9, f"📊 Win Rate por Equipo (mín. {min_partidos} partidos)", alto=460)
        fig9.update_layout(xaxis_title="% Victorias", yaxis_title="")
        mostrar(fig9)

    # --- Gráfica 10: Diferencia de goles (treemap) ---
    est_positivo = est[est["Partidos"] >= 50].copy()
    est_positivo["DifLabel"] = est_positivo["DifGoles"].apply(
        lambda x: f"+{x:.0f}" if x >= 0 else f"{x:.0f}"
    )
    est_positivo["Color"] = est_positivo["DifGoles"]

    fig10 = px.treemap(
        est_positivo,
        path=["Equipo"],
        values="GF",
        color="DifGoles",
        color_continuous_scale=["#ef4444", "#161b22", "#10b981"],
        color_continuous_midpoint=0,
        custom_data=["Equipo", "GF", "GC", "DifGoles", "Partidos"],
    )
    fig10.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Goles marcados: <b>%{customdata[1]:.0f}</b><br>"
            "Goles recibidos: <b>%{customdata[2]:.0f}</b><br>"
            "Diferencia: <b>%{customdata[3]:+.0f}</b><br>"
            "Partidos: <b>%{customdata[4]:.0f}</b>"
            "<extra></extra>"
        ),
        textfont=dict(size=12),
    )
    fig10 = estilizar(fig10, "🌳 Treemap: Goles Marcados y Diferencia de Goles por Equipo", alto=420)
    fig10.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    mostrar(fig10)


# ─────────────────────────────────────────────────────────────────────────────
#  PESTAÑA 4 — EFICIENCIA OFENSIVA
# ─────────────────────────────────────────────────────────────────────────────

with tab4:

    df_tiros = dff.dropna(subset=[
        "HomeTeamShots", "HomeTeamShotsOnTarget",
        "AwayTeamShots", "AwayTeamShotsOnTarget",
    ]).copy()

    # Filtrar ceros para evitar división por cero
    df_tiros = df_tiros[
        (df_tiros["HomeTeamShots"] > 0) &
        (df_tiros["AwayTeamShots"] > 0) &
        (df_tiros["HomeTeamShotsOnTarget"] > 0) &
        (df_tiros["AwayTeamShotsOnTarget"] > 0)
    ]

    col_a, col_b = st.columns(2)

    with col_a:
        # --- Gráfica 11: Scatter tiros vs goles por equipo ---
        ef_equipo = (
            df_tiros.groupby("HomeTeam")
            .agg(
                PromTiros=("HomeTeamShots", "mean"),
                PromAlArco=("HomeTeamShotsOnTarget", "mean"),
                PromGoles=("FullTimeHomeTeamGoals", "mean"),
                Partidos=("HomeTeamShots", "count"),
            )
            .reset_index()
            .rename(columns={"HomeTeam": "Equipo"})
        )

        fig11 = px.scatter(
            ef_equipo,
            x="PromTiros", y="PromGoles",
            size="Partidos",
            color="PromAlArco",
            color_continuous_scale=["#1a1f2e", "#2563eb", ACENTO, "#f0f6fc"],
            text="Equipo",
            custom_data=["Equipo", "PromTiros", "PromAlArco", "PromGoles", "Partidos"],
        )
        fig11.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Tiros/partido: <b>%{customdata[1]:.1f}</b><br>"
                "Al arco/partido: <b>%{customdata[2]:.1f}</b><br>"
                "Goles/partido: <b>%{customdata[3]:.2f}</b><br>"
                "Partidos: <b>%{customdata[4]}</b>"
                "<extra></extra>"
            ),
            textposition="top center",
            textfont=dict(size=9, color="#8b949e"),
            marker=dict(line=dict(color="#30363d", width=1)),
        )
        # Línea de tendencia
        if len(ef_equipo) > 2:
            z = np.polyfit(ef_equipo["PromTiros"], ef_equipo["PromGoles"], 1)
            p = np.poly1d(z)
            x_rng = np.linspace(ef_equipo["PromTiros"].min(), ef_equipo["PromTiros"].max(), 100)
            fig11.add_trace(go.Scatter(
                x=x_rng, y=p(x_rng),
                mode="lines", name="Tendencia",
                line=dict(color="#f59e0b", width=2, dash="dash"),
                hoverinfo="skip",
            ))
        fig11 = estilizar(fig11, "🎯 Tiros vs Goles por Equipo (como Local)", alto=400)
        fig11.update_layout(
            xaxis_title="Tiros promedio/partido",
            yaxis_title="Goles promedio/partido",
        )
        mostrar(fig11)

    with col_b:
        # --- Gráfica 12: Precisión de tiro por temporada (local vs visitante) ---
        prec_temporada = (
            df_tiros.groupby("Season")
            .agg(
                PrecLocal=(
                    "HomeTeamShotsOnTarget",
                    lambda x: (x.sum() / df_tiros.loc[x.index, "HomeTeamShots"].sum() * 100),
                ),
                PrecVisita=(
                    "AwayTeamShotsOnTarget",
                    lambda x: (x.sum() / df_tiros.loc[x.index, "AwayTeamShots"].sum() * 100),
                ),
            )
            .reset_index()
        )
        prec_temporada["Temporada"] = prec_temporada["Season"].str[-4:]

        fig12 = go.Figure()
        for col, nombre, color in [
            ("PrecLocal",  "Local",     ACENTO),
            ("PrecVisita", "Visitante", "#7c3aed"),
        ]:
            fig12.add_trace(go.Scatter(
                x=prec_temporada["Temporada"],
                y=prec_temporada[col],
                mode="lines+markers",
                name=nombre,
                line=dict(color=color, width=2),
                marker=dict(size=6),
                customdata=prec_temporada[["Season", col]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    f"{nombre}: <b>%{{customdata[1]:.1f}}% de precisión</b>"
                    "<extra></extra>"
                ),
            ))
        fig12 = estilizar(fig12, "🎯 Precisión de Tiro por Temporada (%)", alto=400)
        fig12.update_layout(xaxis_title="Temporada", yaxis_title="% Tiros al arco / Total tiros")
        mostrar(fig12)

    # --- Gráfica 13: Córneres vs goles (scatter por partido) ---
    df_corner = dff.dropna(subset=["HomeTeamCorners", "AwayTeamCorners"]).copy()

    if len(df_corner) > 50:
        df_corner["TotalCorners"] = df_corner["HomeTeamCorners"] + df_corner["AwayTeamCorners"]

        fig13 = px.scatter(
            df_corner,
            x="TotalCorners", y="TotalGoles",
            color="ResultadoLabel",
            color_discrete_map={
                "Local gana":     ACENTO,
                "Empate":         "#f59e0b",
                "Visitante gana": "#7c3aed",
            },
            opacity=0.4,
            custom_data=["HomeTeam", "AwayTeam", "Season",
                         "TotalCorners", "TotalGoles", "ResultadoLabel"],
        )
        fig13.update_traces(
            marker=dict(size=5),
            hovertemplate=(
                "<b>%{customdata[0]} vs %{customdata[1]}</b><br>"
                "Temporada: %{customdata[2]}<br>"
                "Córneres: <b>%{customdata[3]}</b><br>"
                "Goles: <b>%{customdata[4]}</b><br>"
                "Resultado: <b>%{customdata[5]}</b>"
                "<extra></extra>"
            ),
        )
        fig13 = estilizar(fig13, "🚩 Córneres Totales vs Goles por Partido", alto=400)
        fig13.update_layout(
            xaxis_title="Total córneres en el partido",
            yaxis_title="Total goles en el partido",
        )
        mostrar(fig13)


# ─────────────────────────────────────────────────────────────────────────────
#  PESTAÑA 5 — MEDIO TIEMPO
# ─────────────────────────────────────────────────────────────────────────────

with tab5:

    df_mt = dff.dropna(subset=["HalfTimeHomeTeamGoals", "HalfTimeAwayTeamGoals"]).copy()

    col_a, col_b = st.columns(2)

    with col_a:
        # --- Gráfica 14: Sankey medio tiempo → resultado final ---
        mapa_mt = {"L": "Local al MT", "E": "Empate al MT", "V": "Visitante al MT"}
        mapa_ft = {"H": "Local gana", "D": "Empate", "A": "Visitante gana"}

        flujos = (
            df_mt.groupby(["ResultadoMT", "FullTimeResult"])
            .size()
            .reset_index(name="Flujo")
        )
        flujos["OrigenLabel"] = flujos["ResultadoMT"].map(mapa_mt)
        flujos["DestinoLabel"] = flujos["FullTimeResult"].map(mapa_ft)

        nodos = list(flujos["OrigenLabel"].unique()) + list(flujos["DestinoLabel"].unique())
        nodo_idx = {n: i for i, n in enumerate(nodos)}
        colores_nodo = [
            ACENTO if "Local" in n else "#7c3aed" if "Visitante" in n else "#f59e0b"
            for n in nodos
        ]

        fig14 = go.Figure(go.Sankey(
            node=dict(
                label=nodos,
                color=colores_nodo,
                pad=20, thickness=20,
            ),
            link=dict(
                source=[nodo_idx[r] for r in flujos["OrigenLabel"]],
                target=[nodo_idx[r] for r in flujos["DestinoLabel"]],
                value=flujos["Flujo"],
                color="rgba(56,217,245,0.15)",
                customdata=flujos[["OrigenLabel", "DestinoLabel", "Flujo"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b> → <b>%{customdata[1]}</b><br>"
                    "Partidos: <b>%{customdata[2]:,}</b>"
                    "<extra></extra>"
                ),
            ),
        ))
        fig14 = estilizar(fig14, "🔀 Sankey: Resultado al Medio Tiempo → Resultado Final", alto=420)
        fig14.update_layout(font=dict(size=12, color="#c9d1d9"))
        mostrar(fig14)

    with col_b:
        # --- Gráfica 15: Barras agrupadas — probabilidad de mantener resultado al MT ---
        mantiene = []
        for r_mt, r_ft, etiqueta in [
            ("L", "H", "Local gana al MT"),
            ("E", "D", "Empate al MT"),
            ("V", "A", "Visitante gana al MT"),
        ]:
            sub = df_mt[df_mt["ResultadoMT"] == r_mt]
            pct_mantiene = (sub["FullTimeResult"] == r_ft).mean() * 100
            pct_revierte = 100 - pct_mantiene
            mantiene.append({
                "Situación": etiqueta,
                "Mantiene": round(pct_mantiene, 1),
                "Revierte": round(pct_revierte, 1),
                "Total": len(sub),
            })
        df_mantiene = pd.DataFrame(mantiene)

        fig15 = go.Figure()
        fig15.add_trace(go.Bar(
            name="Mantiene resultado",
            x=df_mantiene["Situación"],
            y=df_mantiene["Mantiene"],
            marker_color="#10b981",
            customdata=df_mantiene[["Situación", "Mantiene", "Total"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Mantiene: <b>%{customdata[1]:.1f}%</b><br>"
                "Partidos analizados: <b>%{customdata[2]:,}</b>"
                "<extra></extra>"
            ),
        ))
        fig15.add_trace(go.Bar(
            name="Resultado cambia",
            x=df_mantiene["Situación"],
            y=df_mantiene["Revierte"],
            marker_color="#ef4444",
            customdata=df_mantiene[["Situación", "Revierte", "Total"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Cambia: <b>%{customdata[1]:.1f}%</b><br>"
                "Partidos analizados: <b>%{customdata[2]:,}</b>"
                "<extra></extra>"
            ),
        ))
        fig15.update_layout(barmode="stack")
        fig15 = estilizar(fig15, "⏱ ¿Se Mantiene el Resultado del Descanso?", alto=420)
        fig15.update_layout(yaxis_title="% Partidos", xaxis_title="")
        mostrar(fig15)

    # --- Gráfica 16: Goles por tiempo (primer vs segundo) por temporada ---
    goles_x_tiempo = (
        df_mt.groupby("Season")
        .agg(
            GolesHT=("GTMedio", "sum"),
            GolesFT=("TotalGoles", "sum"),
            Partidos=("TotalGoles", "count"),
        )
        .reset_index()
    )
    goles_x_tiempo["GolesST"] = goles_x_tiempo["GolesFT"] - goles_x_tiempo["GolesHT"]
    goles_x_tiempo["PctPrimerTiempo"]  = (goles_x_tiempo["GolesHT"] / goles_x_tiempo["GolesFT"] * 100).round(1)
    goles_x_tiempo["PctSegundoTiempo"] = (goles_x_tiempo["GolesST"] / goles_x_tiempo["GolesFT"] * 100).round(1)
    goles_x_tiempo["Temporada"] = goles_x_tiempo["Season"].str[-4:]

    fig16 = go.Figure()
    for col, nombre, color in [
        ("PctPrimerTiempo",  "1er Tiempo", "#f59e0b"),
        ("PctSegundoTiempo", "2do Tiempo", ACENTO),
    ]:
        fig16.add_trace(go.Scatter(
            x=goles_x_tiempo["Temporada"],
            y=goles_x_tiempo[col],
            mode="lines+markers",
            name=nombre,
            line=dict(color=color, width=2),
            marker=dict(size=6),
            customdata=goles_x_tiempo[["Season", "PctPrimerTiempo", "PctSegundoTiempo", "Partidos"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "1er tiempo: <b>%{customdata[1]:.1f}%</b>  "
                "2do tiempo: <b>%{customdata[2]:.1f}%</b><br>"
                "Partidos: %{customdata[3]}"
                "<extra></extra>"
            ),
        ))
    fig16.add_hline(y=50, line_dash="dot", line_color="#30363d")
    fig16 = estilizar(fig16, "⌚ % de Goles en Cada Tiempo por Temporada", alto=380)
    fig16.update_layout(xaxis_title="Temporada", yaxis_title="% de goles en ese tiempo")
    mostrar(fig16)


# =============================================================================
#  PIE DE PÁGINA
# =============================================================================

st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:#30363d;font-size:0.8rem'>"
    f"Premier League Analytics v2.0 · 1993–2025 · "
    f"{len(dff):,} partidos filtrados de {len(df):,} totales</p>",
    unsafe_allow_html=True,
)