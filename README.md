# Premier League Analytics Dashboard

Dashboard interactivo de análisis estadístico de la Premier League (1993–2025), construido con **Python**, **Streamlit** y **Plotly**.

## Vista previa

El dashboard cuenta con **16 gráficas interactivas** organizadas en 5 pestañas temáticas:

| Pestaña | Contenido |
|---|---|
|  Resultados & Tendencias | Barras apiladas, línea % victorias local, torta global |
|  Goles | Evolución temporal, histograma, violin, heatmap por jornada |
|  Equipos | Top 15 victorias, win rate, treemap diferencia de goles |
|  Eficiencia | Tiros vs goles, precisión de tiro, córneres vs goles |
|  Medio Tiempo | Sankey MT→FT, estabilidad del resultado, goles por tiempo |

##  Estructura del proyecto

```
premier-league-analytics/
├── app.py                  # Aplicación principal de Streamlit
├── PremierLeague.csv       # Dataset (32 temporadas, 12,160 partidos)
├── requirements.txt        # Dependencias de Python
└── README.md               # Este archivo
```

##  Instalación y uso

### 1. Clona el repositorio
```bash
git clone https://github.com/TU_USUARIO/premier-league-analytics.git
cd premier-league-analytics
```

### 2. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecuta la app
```bash
python -m streamlit run app.py
```

La app se abrirá en tu navegador en `http://localhost:8501`

## 📦 Requisitos

- Python 3.8 o superior
- Ver `requirements.txt` para las librerías necesarias

## 📁 Dataset

El dataset `PremierLeague.csv` contiene información de **12,160 partidos** de la Premier League desde la temporada 1993-94 hasta 2024-25, incluyendo:

- Resultados a tiempo completo y medio tiempo
- Goles por equipo
- Tiros totales y al arco
- Córneres y tarjetas
- Cuotas de apuestas (Bet365)

## 🛠 Tecnologías

- [Streamlit](https://streamlit.io/) — Framework del dashboard
- [Plotly](https://plotly.com/python/) — Gráficas interactivas
- [Pandas](https://pandas.pydata.org/) — Manipulación de datos
- [NumPy](https://numpy.org/) — Cálculos numéricos

## 👤 Autor

Desarrollado como proyecto de análisis de datos deportivos.
