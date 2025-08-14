"""
Componente del mapa mundial interactivo para mostrar circuitos de F1
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional
import logging

from config import MAP_CONFIG, COLORS

logger = logging.getLogger(__name__)


class WorldMapComponent:
    """Componente para el mapa mundial de circuitos F1"""

    def __init__(self):
        self.map_config = MAP_CONFIG.copy()

    def create_circuits_map(self, circuits_df: pd.DataFrame, races_df: Optional[pd.DataFrame] = None,
                            selected_year: Optional[int] = None) -> go.Figure:
        """
        Crea el mapa mundial con todos los circuitos

        Args:
            circuits_df: DataFrame con información de circuitos
            races_df: DataFrame con carreras de la temporada seleccionada
            selected_year: Año seleccionado para filtrar

        Returns:
            Figure de Plotly con el mapa
        """
        try:
            fig = go.Figure()

            if circuits_df.empty:
                logger.warning("No hay datos de circuitos disponibles")
                return self._create_empty_map()

            # Filtrar circuitos si hay datos de carreras del año seleccionado
            if races_df is not None and not races_df.empty and selected_year:
                active_circuits = races_df['circuitId'].unique()
                circuits_display = circuits_df[circuits_df['circuitId'].isin(active_circuits)].copy()
                marker_color = COLORS['primary']
                marker_size = 12
            else:
                circuits_display = circuits_df.copy()
                marker_color = COLORS['text_light']
                marker_size = 8

            # Preparar datos para el hover
            hover_text = []
            for _, circuit in circuits_display.iterrows():
                hover_info = f"""
                <b>{circuit['circuitName']}</b><br>
                📍 {circuit['locality']}, {circuit['country']}<br>
                🏁 Circuit ID: {circuit['circuitId']}<br>
                🔗 Click para ver detalles
                """
                hover_text.append(hover_info)

            # Agregar markers de circuitos
            fig.add_trace(go.Scattermapbox(
                lat=circuits_display['lat'],
                lon=circuits_display['long'],
                mode='markers',
                marker=dict(
                    size=marker_size,
                    color=marker_color,
                    opacity=0.8,
                    sizemode='diameter'
                ),
                text=circuits_display['circuitId'],  # Para identificar en callbacks
                hovertext=hover_text,
                hoverinfo='text',
                name='Circuitos F1',
                customdata=circuits_display[['circuitId', 'circuitName', 'country']].values
            ))

            # Configurar el layout del mapa
            fig.update_layout(
                mapbox=dict(
                    style=self.map_config['mapbox_style'],
                    center=dict(
                        lat=self.map_config['center']['lat'],
                        lon=self.map_config['center']['lon']
                    ),
                    zoom=self.map_config['zoom']
                ),
                height=self.map_config['height'],
                margin=dict(l=0, r=0, t=30, b=0),
                title=dict(
                    text=f"Circuitos de Fórmula 1 {selected_year or 'Todos'}",
                    x=0.5,
                    font=dict(size=20, color=COLORS['text'])
                ),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

            return fig

        except Exception as e:
            logger.error(f"Error creando mapa de circuitos: {e}")
            return self._create_empty_map()

    def create_circuit_detail_map(self, circuit_info: Dict, races_info: Optional[List[Dict]] = None) -> go.Figure:
        """
        Crea un mapa detallado de un circuito específico

        Args:
            circuit_info: Información del circuito seleccionado
            races_info: Lista de carreras en este circuito

        Returns:
            Figure de Plotly con el mapa detallado
        """
        try:
            fig = go.Figure()

            lat = circuit_info.get('lat', 0)
            lon = circuit_info.get('lng', 0)

            # Marker principal del circuito
            fig.add_trace(go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode='markers',
                marker=dict(
                    size=20,
                    color=COLORS['primary'],
                    opacity=1.0,
                    symbol='circle'
                ),
                text=[circuit_info.get('circuitName', 'Circuito')],
                hovertext=f"""
                <b>{circuit_info.get('circuitName', 'Circuito')}</b><br>
                📍 {circuit_info.get('locality', '')}, {circuit_info.get('country', '')}<br>
                """,
                hoverinfo='text',
                name='Circuito Principal'
            ))

            # Configurar vista centrada en el circuito
            fig.update_layout(
                mapbox=dict(
                    style='satellite',  # Vista satelital para más detalle
                    center=dict(lat=lat, lon=lon),
                    zoom=15
                ),
                height=400,
                margin=dict(l=0, r=0, t=30, b=0),
                title=dict(
                    text=circuit_info.get('circuitName', 'Circuito Detallado'),
                    x=0.5,
                    font=dict(size=16, color=COLORS['text'])
                ),
                showlegend=False
            )

            return fig

        except Exception as e:
            logger.error(f"Error creando mapa detallado: {e}")
            return self._create_empty_map()

    def _create_empty_map(self) -> go.Figure:
        """Crea un mapa vacío cuando no hay datos"""
        fig = go.Figure()

        fig.update_layout(
            mapbox=dict(
                style=self.map_config['mapbox_style'],
                center=self.map_config['center'],
                zoom=self.map_config['zoom']
            ),
            height=self.map_config['height'],
            margin=dict(l=0, r=0, t=30, b=0),
            title=dict(
                text="Mapa de Circuitos F1 - Cargando datos...",
                x=0.5,
                font=dict(size=20, color=COLORS['text_light'])
            ),
            showlegend=False
        )

        return fig

    def add_race_markers(self, fig: go.Figure, races_data: List[Dict]) -> go.Figure:
        """
        Agrega marcadores adicionales para carreras específicas

        Args:
            fig: Figure existente
            races_data: Lista de datos de carreras

        Returns:
            Figure actualizada
        """
        try:
            if not races_data:
                return fig

            for race in races_data:
                circuit_info = race.get('circuit_info', {})
                if not circuit_info:
                    continue

                # Agregar información de la fecha de carrera
                race_date = race.get('date', '')
                hover_text = f"""
                <b>{race.get('raceName', 'Carrera')}</b><br>
                📅 {race_date}<br>
                🏁 {circuit_info.get('circuitName', '')}<br>
                📍 {circuit_info.get('locality', '')}, {circuit_info.get('country', '')}
                """

                fig.add_trace(go.Scattermapbox(
                    lat=[circuit_info.get('lat')],
                    lon=[circuit_info.get('lng')],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=COLORS['accent'],
                        opacity=0.7,
                        symbol='circle'
                    ),
                    hovertext=hover_text,
                    hoverinfo='text',
                    name=f"Carrera {race.get('round', '')}"
                ))

            return fig

        except Exception as e:
            logger.error(f"Error agregando marcadores de carrera: {e}")
            return fig

    def get_circuit_bounds(self, circuits_df: pd.DataFrame) -> Dict:
        """
        Calcula los límites geográficos para centrar el mapa

        Args:
            circuits_df: DataFrame con circuitos

        Returns:
            Diccionario con límites lat/lon
        """
        if circuits_df.empty:
            return self.map_config['center']

        try:
            bounds = {
                'lat_min': circuits_df['lat'].min(),
                'lat_max': circuits_df['lat'].max(),
                'lon_min': circuits_df['lng'].min(),
                'lon_max': circuits_df['lng'].max(),
                'center_lat': circuits_df['lat'].mean(),
                'center_lon': circuits_df['lng'].mean()
            }

            return bounds

        except Exception as e:
            logger.error(f"Error calculando límites: {e}")
            return self.map_config['center']


# Instancia global del componente
world_map_component = WorldMapComponent()