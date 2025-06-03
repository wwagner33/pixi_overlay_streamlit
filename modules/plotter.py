# modules/plotter.py

import geopandas as gpd
import math

def safe_value(val):
    if isinstance(val, float) and math.isnan(val):
        return None
    # Garante que valores geometry não entrem nas propriedades!
    if hasattr(val, "__geo_interface__"):
        return None
    return val

def safe_dict(row):
    # Exclui campos 'geometry' e 'geom' das propriedades
    exclui = {"geometry", "geom"}
    return {col: safe_value(row[col]) for col in row.index if col not in exclui}

def preparar_geojson_para_pixi(gdf: gpd.GeoDataFrame, regiao: str):
    region_gdf = gdf[gdf["regiao_administrativa"] == regiao]
    features = []
    for _, row in region_gdf.iterrows():
        props = safe_dict(row)
        feature = {
            "type": "Feature",
            "geometry": row.geometry.__geo_interface__,
            "properties": props
        }
        features.append(feature)
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson
