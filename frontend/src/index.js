import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { Streamlit } from "streamlit-component-lib";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

Streamlit.setComponentReady();
