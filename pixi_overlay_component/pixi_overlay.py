import os
import streamlit.components.v1 as components

_RELEASE = False

if not _RELEASE:
    _pixi_overlay = components.declare_component(
        "pixi_overlay_streamlit", url="http://localhost:3000"
    )
else:
    build_dir = os.path.join(os.path.dirname(__file__), "../frontend/build")
    _pixi_overlay = components.declare_component(
        "pixi_overlay_streamlit", path=build_dir
    )

def pixi_overlay(data=None, key=None, **kwargs):
    """
    Exibe o componente PixiOverlay.
    data: GeoJSON dict
    key: chave do Streamlit
    kwargs: argumentos extras futuros
    """
    return _pixi_overlay(data=data, key=key, default=None, **kwargs)
