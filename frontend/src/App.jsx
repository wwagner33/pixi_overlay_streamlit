import React, { useEffect, useRef } from "react";
import L from "leaflet";
import * as PIXI from "pixi.js";
import "leaflet/dist/leaflet.css";
import "leaflet-pixi-overlay";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

// CORES igual do seu Python
const CORES = {
  "Minifúndio": "#9b19f5",
  "Pequena Propriedade": "#0040bf",
  "Média Propriedade": "#e6d800",
  "Grande Propriedade": "#d97f00",
  "Sem Classificação": "#808080"
};

function desenharPoligonos(geojson, pixiContainer) {
  // Limpa o container antes de desenhar
  pixiContainer.removeChildren();

  geojson.features.forEach(feature => {
    const cor = CORES[feature.properties.categoria] || "#888";
    const coords = feature.geometry.coordinates;

    // Suporte a MultiPolygon ou Polygon
    const polygons = feature.geometry.type === "Polygon" ? [coords] : coords;

    polygons.forEach(polygon => {
      const graphics = new PIXI.Graphics();
      graphics.lineStyle(1, 0x000000, 1); // borda preta
      graphics.beginFill(PIXI.utils.string2hex(cor), 0.7);

      polygon.forEach(ring => {
        ring.forEach(([lng, lat], idx) => {
          // Converta para local no mapa usando leaflet
          const { x, y } = window.leafletUtils.latLngToLayerPoint([lat, lng]);
          if (idx === 0) {
            graphics.moveTo(x, y);
          } else {
            graphics.lineTo(x, y);
          }
        });
        graphics.closePath();
      });

      graphics.endFill();
      pixiContainer.addChild(graphics);
    });
  });
}

const App = ({ args }) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const pixiContainerRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current).setView([-5, -39], 7);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(mapRef.current);

      // Função utilitária global para conversão
      window.leafletUtils = {};
      window.leafletUtils.latLngToLayerPoint = latLng =>
        mapRef.current.latLngToLayerPoint(latLng);

      pixiContainerRef.current = new PIXI.Container();

      const pixiOverlay = L.pixiOverlay((utils) => {
        window.leafletUtils.latLngToLayerPoint = utils.latLngToLayerPoint;
        if (args.data) {
          desenharPoligonos(args.data, pixiContainerRef.current);
        }
        utils.getRenderer().render(pixiContainerRef.current);
      }, pixiContainerRef.current).addTo(mapRef.current);
    }
  }, []);

  // Redesenha se os dados mudarem
  useEffect(() => {
    if (mapRef.current && pixiContainerRef.current && args.data) {
      desenharPoligonos(args.data, pixiContainerRef.current);
    }
  }, [args.data]);

  return <div ref={mapContainerRef} style={{ width: "100%", height: "700px" }} />;
};

export default withStreamlitConnection(App);
