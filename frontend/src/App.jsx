import React, { useEffect, useRef } from "react";
import { Streamlit } from "streamlit-component-lib";
import L from "leaflet";
import * as PIXI from "pixi.js";
import "leaflet/dist/leaflet.css";
import "leaflet-pixi-overlay";

const App = () => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map(mapContainerRef.current).setView([-3.7, -38.5], 12);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "OpenStreetMap",
      }).addTo(mapRef.current);

      const pixiContainer = new PIXI.Container();
      const pixiOverlay = L.pixiOverlay((utils) => {
        const renderer = utils.getRenderer();
        renderer.render(pixiContainer);
      }, pixiContainer).addTo(mapRef.current);

      // Exemplo de objeto Pixi.js
      const graphics = new PIXI.Graphics();
      graphics.beginFill(0xff0000, 0.8);
      graphics.drawCircle(0, 0, 20);
      graphics.endFill();
      pixiContainer.addChild(graphics);

      pixiOverlay.redraw();
    }
  }, []);

  return (
    <div
      ref={mapContainerRef}
      style={{ width: "100%", height: "500px", margin: "0 auto" }}
    />
  );
};

export default App;
