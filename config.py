"""
Configuración general del proyecto F1 Dashboard
"""

import os
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"

# Configuración de la aplicación
APP_CONFIG = {
    'debug': True,
    'host': '127.0.0.1',
    'port': 8050,
    'title': 'F1 Dashboard Interactivo'
}

# Configuración de colores (tema F1)
COLORS = {
    'primary': '#E10600',      # Rojo F1
    'secondary': '#15151E',    # Negro F1
    'accent': '#FF6600',       # Naranja
    'background': '#FFFFFF',   # Blanco
    'text': '#15151E',         # Texto principal
    'text_light': '#6B7280',   # Texto secundario
    'success': '#10B981',      # Verde
    'warning': '#F59E0B',      # Amarillo
    'error': '#EF4444'         # Rojo error
}

# Configuración de mapas
MAP_CONFIG = {
    'mapbox_style': 'open-street-map',
    'zoom': 2,
    'center': {'lat': 30, 'lon': 0},
    'height': 600
}

# Configuración de gráficos 3D
PLOT_3D_CONFIG = {
    'height': 700,
    'showlegend': True,
    'scene': {
        'camera': {
            'eye': {'x': 1.2, 'y': 1.2, 'z': 0.6}
        }
    }
}

