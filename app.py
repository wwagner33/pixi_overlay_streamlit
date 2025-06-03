# app.py

import streamlit as st
from modules.data_loader import (
    fetch_regioes,
    fetch_municipios,
    fetch_geojson_por_regiao,
    fetch_geojson_por_municipio
)
from streamlit.components.v1 import html
import json

st.set_page_config(
    page_title="ccTerra::Análise da Concentração Fundiária do Ceará",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Mapa Fundiário Interativo com PixiOverlay 🚜")

# 1) Busca lista de regiões do microserviço
regioes = fetch_regioes()
if not regioes:
    st.error("Não foi possível carregar as regiões do microserviço.")
    st.stop()

# 2) Usuário escolhe região
regiao = st.selectbox("Selecione a região administrativa", regioes)

# 3) Busca municípios dessa região
municipios = fetch_municipios(regiao)
# Adiciona opção para “mostrar toda a região”
municipio = st.selectbox(
    "Selecione o município (opcional)", ["(toda a região)"] + municipios
)

# 4) Quando o usuário clicar em “Gerar Mapa”, fazemos a chamada correspondente
geojson = None
if st.button("Gerar Mapa"):
    if municipio == "(toda a região)":
        # chama /geojson?regiao=regiao
        try:
            geojson = fetch_geojson_por_regiao(regiao)
        except Exception as e:
            st.error(f"Não foi possível carregar GeoJSON da região '{regiao}':\n{e}")
            st.stop()
    else:
        # chama /geojson?municipio=municipio
        try:
            geojson = fetch_geojson_por_municipio(municipio)
        except Exception as e:
            st.error(f"Não foi possível carregar GeoJSON do município '{municipio}':\n{e}")
            st.stop()

    # Se retornou GeoJSON vazio ou sem features:
    if not geojson or not geojson.get("features"):
        st.warning("Nenhuma geometria encontrada para o filtro selecionado.")
        st.stop()

    # 5) Converte para string JSON para injetar no HTML do PixiOverlay
    geojson_str = json.dumps(geojson)

    # 6) Cores para categorias (deve coincidir com o que está no backend)
    CORES = {
        "Pequena Propriedade < 1 MF": "#9b19f5",
        "Pequena Propriedade": "#0040bf",
        "Média Propriedade": "#e6d800",
        "Grande Propriedade": "#d97f00",
        "Sem Classificação": "#808080"
    }

    # 7) Monta o HTML/JavaScript que cria o Leaflet+PixiOverlay
    html_code = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>PixiOverlay Example</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <style>
          html, body, #map {{ height: 100%; margin: 0; padding: 0; }}
        </style>
      </head>
      <body>
        <div id="map" style="width: 100%; height: 700px;"></div>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pixi.js/5.3.10/pixi.min.js"></script>
        <script src="https://unpkg.com/leaflet-pixi-overlay@1.9.4/L.PixiOverlay.min.js"></script>
        <script>
          const CORES = {json.dumps(CORES)};
          const geojson = {geojson_str};

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
            attribution: "© OpenStreetMap"
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
