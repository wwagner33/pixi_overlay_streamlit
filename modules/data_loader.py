# modules/data_loader.py

import requests
import streamlit as st

# URL base do seu microserviço (ajuste se estiver rodando em outro host/porta)
BASE_URL = st.secrets.get("TERRAGEO_URL", "http://127.0.0.1:8000")


@st.cache_data(ttl=60 * 5)  # cacheia por 5 minutos
def fetch_regioes() -> list[str]:
    """
    Chama GET /regioes no microserviço e retorna a lista de regiões.
    """
    resp = requests.get(f"{BASE_URL}/regioes")
    resp.raise_for_status()
    data = resp.json()
    return data.get("regioes", [])


@st.cache_data(ttl=60 * 5)
def fetch_municipios(regiao: str) -> list[str]:
    """
    Chama GET /municipios?regiao=XYZ e retorna a lista de municípios.
    """
    resp = requests.get(f"{BASE_URL}/municipios", params={"regiao": regiao})
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    data = resp.json()
    return data.get("municipios", [])


@st.cache_data(ttl=60 * 5)
def fetch_geojson_por_regiao(regiao: str) -> dict:
    """
    Chama GET /geojson?regiao=XYZ e retorna o FeatureCollection.
    """
    resp = requests.get(f"{BASE_URL}/geojson", params={"regiao": regiao})
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=60 * 5)
def fetch_geojson_por_municipio(municipio: str) -> dict:
    """
    Chama GET /geojson?municipio=YYY e retorna o FeatureCollection.
    """
    resp = requests.get(f"{BASE_URL}/geojson", params={"municipio": municipio})
    resp.raise_for_status()
    return resp.json()
