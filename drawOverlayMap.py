# drawOverlayMap.py

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
        "Pequena Propriedade < 1 MF": "#fecc5c",
        "Pequena Propriedade": "#fd8d3c",
        "Média Propriedade": "#f03b20",
        "Grande Propriedade": "#bd0026",
        "Sem Classificação": "#808080"
    }

    # 7) Monta o HTML/JavaScript completo com controles interativos
    html_code = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Mapa Fundiário Interativo</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
          html, body, #map {{ height: 100%; margin: 0; padding: 0; }}
          
          /* ESTILOS DA LEGENDA INTERATIVA */
          #legend {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ddd;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            font-family: Arial, sans-serif;
            max-width: 250px;
          }}
          #legend h4 {{
            margin: 0 0 12px 0;
            text-align: center;
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
          }}
          .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            padding: 5px;
            border-radius: 4px;
            transition: background 0.2s;
          }}
          .legend-item:hover {{
            background: #f5f5f5;
          }}
          .legend-color {{
            width: 22px;
            height: 18px;
            margin-right: 10px;
            border: 1px solid #888;
            border-radius: 3px;
          }}
          .legend-controls {{
            margin-left: auto;
            display: flex;
            align-items: center;
          }}
          .toggle-btn {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            color: #666;
            margin-right: 8px;
          }}
          .opacity-slider {{
            width: 60px;
            margin-left: 5px;
          }}
          
          /* Botão de zoom */
          .zoom-to-category {{
            background: #4a90e2;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 2px 8px;
            font-size: 12px;
            cursor: pointer;
            margin-left: 5px;
            transition: background 0.2s;
          }}
          .zoom-to-category:hover {{
            background: #3a7bc8;
          }}
          
          /* Controle de camadas */
          #layer-controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            z-index: 1000;
            font-size: 14px;
          }}
        </style>
      </head>
      <body>
        <div id="map" style="width: 100%; height: 700px;"></div>
        
        <!-- Legenda Interativa -->
        <div id="legend">
          <h4><i class="fas fa-layer-group"></i> Tipos de Propriedade</h4>
          {''.join([
            f'<div class="legend-item" id="legend-{categoria.replace(" ", "_")}">'
            f'<div class="legend-color" style="background:{cor};"></div>'
            f'<span>{categoria}</span>'
            f'<div class="legend-controls">'
            f'<button class="toggle-btn" data-category="{categoria}" title="Mostrar/Ocultar">'
            f'<i class="fas fa-eye"></i>'
            f'</button>'
            f'<input type="range" min="0" max="1" step="0.1" value="0.6" class="opacity-slider" data-category="{categoria}">'
            f'<button class="zoom-to-category" data-category="{categoria}" title="Zoom para Categoria">'
            f'<i class="fas fa-search-plus"></i>'
            f'</button>'
            f'</div>'
            f'</div>'
            for categoria, cor in CORES.items()
          ])}
        </div>
        
        <!-- Controle Global de Camadas -->

        
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pixi.js/5.3.10/pixi.min.js"></script>
        <script src="https://unpkg.com/leaflet-pixi-overlay@1.9.4/L.PixiOverlay.min.js"></script>
        <script>
          const CORES = {json.dumps(CORES)};
          const geojson = {geojson_str};
          let map, pixiOverlay;
          const categoryContainers = {{}};
          const categoryBounds = {{}};

          // Função para calcular o centro do mapa
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

          // Função para extrair coordenadas e calcular bounds
          function extractCoordinates(feature) {{
            const coords = [];
            if (feature.geometry.type === "Polygon") {{
              feature.geometry.coordinates[0].forEach(coord => coords.push([coord[1], coord[0]]));
            }} else if (feature.geometry.type === "MultiPolygon") {{
              feature.geometry.coordinates[0][0].forEach(coord => coords.push([coord[1], coord[0]]));
            }}
            return coords;
          }}

          // Função principal para inicializar o mapa
          function initMap() {{
            const center = getMapCenter(geojson);
            map = L.map('map').setView(center, 10);
            
            L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
              attribution: "© OpenStreetMap"
            }}).addTo(map);

            // Criar container principal
            const mainContainer = new PIXI.Container();
            
            // Criar containers individuais para cada categoria
            Object.keys(CORES).forEach(categoria => {{
              categoryContainers[categoria] = new PIXI.Container();
              categoryContainers[categoria].alpha = 0.6; // Opacidade padrão
              categoryContainers[categoria].visible = true;
              mainContainer.addChild(categoryContainers[categoria]);
              categoryBounds[categoria] = L.latLngBounds();
            }});
            
            // Container para não classificados
            categoryContainers["Sem Classificação"] = new PIXI.Container();
            categoryContainers["Sem Classificação"].alpha = 0.6;
            categoryContainers["Sem Classificação"].visible = true;
            mainContainer.addChild(categoryContainers["Sem Classificação"]);
            categoryBounds["Sem Classificação"] = L.latLngBounds();

            // Criar overlay
            pixiOverlay = L.pixiOverlay(function(utils) {{
              // Limpar containers
              Object.values(categoryContainers).forEach(container => {{
                container.removeChildren();
              }});
              
              // Resetar bounds
              Object.keys(categoryBounds).forEach(key => {{
                categoryBounds[key] = L.latLngBounds();
              }});
              
              // Processar cada feature
              for (const feature of geojson.features) {{
                const categoria = feature.properties.categoria || "Sem Classificação";
                const cor = CORES[categoria] || "#aaa";
                let polygons = [];
                
                if (feature.geometry.type === "Polygon") {{
                  polygons = [feature.geometry.coordinates];
                }} else if (feature.geometry.type === "MultiPolygon") {{
                  polygons = feature.geometry.coordinates;
                }}
                
                for (const polygon of polygons) {{
                  for (const ring of polygon) {{
                    const graphics = new PIXI.Graphics();
                    graphics.lineStyle(0.1, 0x000000, 1);
                    graphics.beginFill(PIXI.utils.string2hex(cor), categoryContainers[categoria].alpha);
                    
                    ring.forEach(([lng, lat], idx) => {{
                      const p = utils.latLngToLayerPoint([lat, lng]);
                      if (idx === 0) {{
                        graphics.moveTo(p.x, p.y);
                      }} else {{
                        graphics.lineTo(p.x, p.y);
                      }}
                      
                      // Atualizar bounds da categoria
                      categoryBounds[categoria].extend([lat, lng]);
                    }});
                    
                    graphics.closePath();
                    graphics.endFill();
                    categoryContainers[categoria].addChild(graphics);
                  }}
                }}
              }}
              utils.getRenderer().render(mainContainer);
            }}, mainContainer).addTo(map);
          }}

          // Inicializar o mapa
          initMap();
          
          // ===== FUNÇÕES DE CONTROLE =====
          
          // Alternar visibilidade da camada
          function toggleLayer(categoria, visible) {{
            if (categoryContainers[categoria]) {{
              categoryContainers[categoria].visible = visible;
              
              // Atualizar ícone do botão
              const icon = document.querySelector(`.toggle-btn[data-category="${{categoria}}"] i`);
              icon.className = visible ? "fas fa-eye" : "fas fa-eye-slash";
              
              pixiOverlay.redraw();
            }}
          }}
          
          // Ajustar opacidade da camada
          function setLayerOpacity(categoria, opacity) {{
            if (categoryContainers[categoria]) {{
              categoryContainers[categoria].alpha = opacity;
              pixiOverlay.redraw();
            }}
          }}
          
          // Zoom para categoria específica
          function zoomToCategory(categoria) {{
            if (categoryBounds[categoria] && !categoryBounds[categoria].isEmpty()) {{
              map.fitBounds(categoryBounds[categoria], {{ 
                padding: [50, 50],
                maxZoom: 15
              }});
            }}
          }}
          
          // Mostrar todas as camadas
          function showAllLayers() {{
            Object.keys(categoryContainers).forEach(categoria => {{
              categoryContainers[categoria].visible = true;
              const icon = document.querySelector(`.toggle-btn[data-category="${{categoria}}"] i`);
              if (icon) icon.className = "fas fa-eye";
            }});
            pixiOverlay.redraw();
          }}
          
          // Ocultar todas as camadas
          function hideAllLayers() {{
            Object.keys(categoryContainers).forEach(categoria => {{
              categoryContainers[categoria].visible = false;
              const icon = document.querySelector(`.toggle-btn[data-category="${{categoria}}"] i`);
              if (icon) icon.className = "fas fa-eye-slash";
            }});
            pixiOverlay.redraw();
          }}
          
          // ===== EVENT LISTENERS =====
          
          // Botões de toggle
          document.querySelectorAll('.toggle-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
              const categoria = this.getAttribute('data-category');
              const currentlyVisible = categoryContainers[categoria].visible;
              toggleLayer(categoria, !currentlyVisible);
            }});
          }});
          
          // Sliders de opacidade
          document.querySelectorAll('.opacity-slider').forEach(slider => {{
            slider.addEventListener('input', function() {{
              const categoria = this.getAttribute('data-category');
              setLayerOpacity(categoria, parseFloat(this.value));
            }});
          }});
          
          // Botões de zoom
          document.querySelectorAll('.zoom-to-category').forEach(btn => {{
            btn.addEventListener('click', function() {{
              const categoria = this.getAttribute('data-category');
              zoomToCategory(categoria);
            }});
          }});
          
          // Controles globais
          document.getElementById('show-all').addEventListener('click', showAllLayers);
          document.getElementById('hide-all').addEventListener('click', hideAllLayers);
        </script>
      </body>
    </html>
    """

    html(html_code, height=800, scrolling=True)
