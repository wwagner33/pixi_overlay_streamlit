import os
import streamlit.components.v1 as components

_RELEASE = False
from .pixi_overlay import pixi_overlay

if not _RELEASE:
    _component_func = components.declare_component(
        "pixi_overlay_streamlit",
        url="http://localhost:3000"
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "pixi_overlay_streamlit", path=build_dir
    )

def pixi_overlay_streamlit(key=None):
    _component_func(key=key, default=None)
