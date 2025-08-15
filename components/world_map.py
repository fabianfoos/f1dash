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

            # Asignar marker_size a circuits_df según si hay carrera en races_df
            marker_size_active = 12
            marker_size_inactive = 8
            active_circuits = set()
            if races_df is not None and not races_df.empty and selected_year:
                races_df['raceDate'] = pd.to_datetime(races_df['raceDate'])
                races_df = races_df[races_df['raceDate'] < pd.to_datetime('today')]
                active_circuits = set(races_df['circuitId'].unique())
                circuits_df['marker_size'] = circuits_df['circuitId'].apply(
                    lambda cid: marker_size_active if cid in active_circuits else marker_size_inactive
                )
                circuits_df['marker_color'] = circuits_df['circuitId'].apply(
                    lambda cid: COLORS['primary'] if cid in active_circuits else COLORS['text_light']
                )
            else:
                circuits_df['marker_size'] = marker_size_inactive
                circuits_df['marker_color'] = COLORS['text_light']

            # Preparar datos para el hover
            hover_text = []
            for _, circuit in circuits_df.iterrows():
                hover_info = f"""
                <b>{circuit['circuitName']}</b><br>
                📍 {circuit['locality']}, {circuit['country']}<br>
                🏁 Circuit ID: {circuit['circuitId']}<br>
                🔗 Click para ver detalles
                """ if circuit['circuitId'] in active_circuits else f"""
                <b>{circuit['circuitName']}</b><br>
                📍 {circuit['locality']}, {circuit['country']}<br>
                🏁 Circuit ID: {circuit['circuitId']}
                """
                hover_text.append(hover_info)

            # Agregar markers de circuitos
            fig.add_trace(go.Scattermapbox(
                lat=circuits_df['lat'],
                lon=circuits_df['long'],
                mode='markers',
                marker=dict(
                    size=circuits_df['marker_size'],
                    color=circuits_df['marker_color'],
                    opacity=0.8,
                    sizemode='diameter'
                ),
                text=circuits_df['circuitId'],  # Para identificar en callbacks
                hovertext=hover_text,
                hoverinfo='text',
                name='Circuitos F1',
                customdata=circuits_df[['circuitId', 'circuitName', 'country']].values
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

# Instancia global del componente
world_map_component = WorldMapComponent()