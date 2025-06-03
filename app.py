import streamlit as st
from modules.data_loader import load_csv_data, validate_data
from modules.plotter import preparar_geojson_para_pixi
from streamlit.components.v1 import html
import json

st.set_page_config(
    page_title="ccTerra::Análise da Concentração Fundiária do Ceará",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Mapa Fundiário Interativo com PixiOverlay 🚜")

BASE_FOLDER = "data"
df = load_csv_data(BASE_FOLDER)
_, _, gdf_inter, _, _ = validate_data(df)

regioes = sorted(gdf_inter["regiao_administrativa"].dropna().unique())
regiao = st.selectbox("Selecione a região administrativa", regioes)
geojson = preparar_geojson_para_pixi(gdf_inter, regiao)
geojson_str = json.dumps(geojson)  # <- Importante: agora é string!

# Cores para categorias (as mesmas do Python)
CORES = {
    "Minifúndio": "#9b19f5",
    "Pequena Propriedade": "#0040bf",
    "Média Propriedade": "#e6d800",
    "Grande Propriedade": "#d97f00",
    "Sem Classificação": "#808080"
}

html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>PixiOverlay Example</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
  <style> html, body, #map {{ height: 100%; margin: 0; padding: 0; }} </style>
</head>
<body>
  <div id="map" style="width: 100%; height: 700px;"></div>
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pixi.js/5.3.10/pixi.min.js"></script>
  <script src="https://unpkg.com/leaflet-pixi-overlay@1.9.4/L.PixiOverlay.min.js"></script>
  <script>
    const CORES = {json.dumps(CORES)};
    const geojson = {geojson_str};

    // Pega centro aproximado do primeiro polígono
    function getMapCenter(geojson) {{
      for (const f of geojson.features) {{
        const g = f.geometry;
        if (g.type === "Polygon") {{
          const [lng, lat] = g.coordinates[0][0];
          return [lat, lng];
        }} else if (g.type === "MultiPolygon") {{
          const [lng, lat] = g.coordinates[0][0][0];
          return [lat, lng];
        }}
      }}
      return [-5.2, -39.0];
    }}

    const map = L.map('map').setView(getMapCenter(geojson), 10);
    L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
      attribution: "OpenStreetMap"
    }}).addTo(map);

    const pixiContainer = new PIXI.Container();
    const pixiOverlay = L.pixiOverlay(function(utils) {{
      pixiContainer.removeChildren();
      for (const feature of geojson.features) {{
        const cor = CORES[feature.properties.categoria] || "#aaa";
        let polygons = [];
        if (feature.geometry.type === "Polygon") {{
          polygons = [feature.geometry.coordinates];
        }} else if (feature.geometry.type === "MultiPolygon") {{
          polygons = feature.geometry.coordinates;
        }}
        for (const polygon of polygons) {{
          for (const ring of polygon) {{
            const graphics = new PIXI.Graphics();
            graphics.lineStyle(1, 0x000000, 1);
            graphics.beginFill(PIXI.utils.string2hex(cor), 0.7);
            ring.forEach(([lng, lat], idx) => {{
              const p = utils.latLngToLayerPoint([lat, lng]);
              if (idx === 0) {{
                graphics.moveTo(p.x, p.y);
              }} else {{
                graphics.lineTo(p.x, p.y);
              }}
            }});
            graphics.closePath();
            graphics.endFill();
            pixiContainer.addChild(graphics);
          }}
        }}
      }}
      utils.getRenderer().render(pixiContainer);
    }}, pixiContainer).addTo(map);
  </script>
</body>
</html>
"""

html(html_code, height=720)
