"""
Componente para visualización 3D de pistas de F1
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

from config import PLOT_3D_CONFIG, COLORS

logger = logging.getLogger(__name__)


class Track3DComponent:
    """Componente para visualización tridimensional de pistas"""

    def __init__(self):
        self.plot_config = PLOT_3D_CONFIG.copy()

    def create_3d_track(self, track_data: Dict, circuit_info: Dict) -> go.Figure:
        """
        Crea visualización 3D completa de una pista

        Args:
            track_data: Datos de coordenadas y elevación
            circuit_info: Información general del circuito

        Returns:
            Figure 3D de Plotly
        """
        try:
            if not track_data:
                return go.Figure()  # figura vacía
            fig = go.Figure()

            #if not track_data or not all(key in track_data for key in ['x', 'y', 'z']):
            #    return self._create_empty_3d_plot(circuit_info.get('circuitName', 'Pista'))

            x_coords = np.array(track_data['x'])
            y_coords = np.array(track_data['y'])
            z_coords = np.array(track_data['z'])

            # Trazado principal de la pista
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                #z=z_coords,
                mode='lines',
                line=dict(color='black', width=6),
                hoverinfo='skip',
                showlegend=False
            ))

            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)

            # Agregar sectores
            #self._add_sectors(fig, track_data, x_coords, y_coords, z_coords)

            # Agregar zonas DRS
            #self._add_drs_zones(fig, track_data, x_coords, y_coords, z_coords)

            # Agregar curvas importantes
            #self._add_turns(fig, track_data, x_coords, y_coords, z_coords)

            # Agregar línea de meta
            self._add_start_finish_line(fig, x_coords, y_coords, z_coords)

            # Configurar layout 3D
            self._configure_3d_layout(fig, circuit_info)

            return fig

        except Exception as e:
            logger.error(f"Error creando visualización 3D: {e}")
            return self._create_empty_3d_plot(circuit_info.get('circuitName', 'Pista'))

    def _add_sectors(self, fig: go.Figure, track_data: Dict, x: np.array, y: np.array, z: np.array):
        """Agrega visualización de sectores"""
        try:
            sectors = track_data.get('sectors', [])

            for i, sector in enumerate(sectors):
                start_idx = sector['start']
                end_idx = sector['end']

                # Asegurar que los índices están dentro del rango
                start_idx = max(0, min(start_idx, len(x) - 1))
                end_idx = max(0, min(end_idx, len(x)))

                sector_x = x[start_idx:end_idx]
                sector_y = y[start_idx:end_idx]
                sector_z = z[start_idx:end_idx] + 2  # Elevar ligeramente para visibilidad

                color_map = {'Sector 1': '#00FF00', 'Sector 2': '#FFFF00', 'Sector 3': '#FF0000'}
                sector_color = color_map.get(sector['name'], '#FFFFFF')

                fig.add_trace(go.Scatter3d(
                    x=sector_x,
                    y=sector_y,
                    z=sector_z,
                    mode='lines',
                    line=dict(
                        color=sector_color,
                        width=4,
                        dash='dash'
                    ),
                    name=sector['name'],
                    hovertemplate=f'<b>{sector["name"]}</b><br>' +
                                  'Inicio: %{x:.0f}m<br>' +
                                  'Fin: %{y:.0f}m<extra></extra>',
                    showlegend=True
                ))

        except Exception as e:
            logger.warning(f"Error agregando sectores: {e}")

    def _add_drs_zones(self, fig: go.Figure, track_data: Dict, x: np.array, y: np.array, z: np.array):
        """Agrega zonas DRS"""
        try:
            drs_zones = track_data.get('drs_zones', [])

            for zone in drs_zones:
                start_idx = max(0, min(zone['start'], len(x) - 1))
                end_idx = max(0, min(zone['end'], len(x)))

                drs_x = x[start_idx:end_idx]
                drs_y = y[start_idx:end_idx]
                drs_z = z[start_idx:end_idx] + 5  # Mayor elevación para destacar

                fig.add_trace(go.Scatter3d(
                    x=drs_x,
                    y=drs_y,
                    z=drs_z,
                    mode='lines',
                    line=dict(
                        color='#00FFFF',
                        width=6,
                        dash='dot'
                    ),
                    name=zone['name'],
                    hovertemplate=f'<b>{zone["name"]}</b><br>' +
                                  'Zona de DRS activo<extra></extra>',
                    showlegend=True
                ))

        except Exception as e:
            logger.warning(f"Error agregando zonas DRS: {e}")

    def _add_turns(self, fig: go.Figure, track_data: Dict, x: np.array, y: np.array, z: np.array):
        """Agrega marcadores de curvas importantes"""
        try:
            turns = track_data.get('turns', [])

            turn_x = []
            turn_y = []
            turn_z = []
            turn_text = []
            turn_colors = []

            difficulty_colors = {
                'easy': '#00FF00',
                'medium': '#FFFF00',
                'hard': '#FF0000'
            }

            for turn in turns:
                pos = min(turn['position'], len(x) - 1)
                turn_x.append(x[pos])
                turn_y.append(y[pos])
                turn_z.append(z[pos] + 8)  # Elevar para visibilidad
                turn_text.append(f"T{turn['number']}")
                turn_colors.append(difficulty_colors.get(turn.get('difficulty', 'medium'), '#FFFF00'))

            if turn_x:
                fig.add_trace(go.Scatter3d(
                    x=turn_x,
                    y=turn_y,
                    z=turn_z,
                    mode='markers+text',
                    marker=dict(
                        size=8,
                        color=turn_colors,
                        symbol='circle',
                        line=dict(width=2, color='#000000')
                    ),
                    text=turn_text,
                    textposition="middle center",
                    textfont=dict(size=10, color='#000000'),
                    name='Curvas',
                    hovertemplate='<b>Curva %{text}</b><br>' +
                                  'Tipo: %{customdata[0]}<br>' +
                                  'Dificultad: %{customdata[1]}<extra></extra>',
                    customdata=[[t.get('type', ''), t.get('difficulty', '')] for t in turns],
                    showlegend=True
                ))

        except Exception as e:
            logger.warning(f"Error agregando curvas: {e}")

    def _add_start_finish_line(self, fig: go.Figure, x: np.array, y: np.array, z: np.array):
        """Agrega línea de salida/meta"""
        try:
            if len(x) > 0:
                # Línea de meta en el punto inicial
                fig.add_trace(go.Scatter(
                    x=[x[0], x[0]],
                    y=[y[0], y[0]],
                    #z=[z[0], z[0] + 15],  # Línea vertical
                    mode='markers',
                    marker=dict(
                        size=15,
                        color="#BE4444",
                        symbol='circle'
                    ),
                    name='Meta',
                    hovertemplate='<b>Línea de Salida/Meta</b><extra></extra>',
                    showlegend=True
                ))

        except Exception as e:
            logger.warning(f"Error agregando línea de meta: {e}")

    def _configure_3d_layout(self, fig: go.Figure, circuit_info: Dict):
        """Configura el layout del gráfico 3D"""
        circuit_name = circuit_info.get('circuitName', 'Circuito F1')

        fig.update_layout(
            title=dict(
                text=f"Vista 3D - {circuit_name}",
                x=0.5,
                font=dict(size=20, color=COLORS['text'])
            ),
            scene=dict(
                xaxis=dict(
                    title='Distancia X (m)',
                    gridcolor='#E5E5E5',
                    showbackground=True,
                    backgroundcolor='rgba(230, 230, 230, 0.5)'
                ),
                yaxis=dict(
                    title='Distancia Y (m)',
                    gridcolor='#E5E5E5',
                    showbackground=True,
                    backgroundcolor='rgba(230, 230, 230, 0.5)'
                ),
                zaxis=dict(
                    title='Elevación (m)',
                    gridcolor='#E5E5E5',
                    showbackground=True,
                    backgroundcolor='rgba(230, 230, 230, 0.5)'
                ),
                camera=self.plot_config['scene']['camera'],
                aspectmode='data'
            ),
            height=self.plot_config['height'],
            showlegend=self.plot_config['showlegend'],
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#E5E5E5',
                borderwidth=1
            ),
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

    def _create_empty_3d_plot(self, title: str = "Pista 3D") -> go.Figure:
        """Crea un gráfico 3D vacío"""
        fig = go.Figure()

        fig.update_layout(
            title=dict(
                text=f"Vista 3D - {title} (Cargando...)",
                x=0.5,
                font=dict(size=20, color=COLORS['text_light'])
            ),
            scene=dict(
                xaxis=dict(title='Distancia X (m)'),
                yaxis=dict(title='Distancia Y (m)'),
                zaxis=dict(title='Elevación (m)'),
                camera=self.plot_config['scene']['camera']
            ),
            height=self.plot_config['height'],
            showlegend=False
        )

        return fig

    def create_elevation_profile(self, track_data: Dict, circuit_info: Dict) -> go.Figure:
        """
        Crea un perfil de elevación de la pista

        Args:
            track_data: Datos de la pista
            circuit_info: Información del circuito

        Returns:
            Figure 2D con el perfil de elevación
        """
        try:
            fig = go.Figure()

            if not track_data or 'z' not in track_data:
                return fig

            z_coords = np.array(track_data['z'])
            distance = np.linspace(0, circuit_info.get('length', len(z_coords)), len(z_coords))

            # Línea principal de elevación
            fig.add_trace(go.Scatter(
                x=distance,
                y=z_coords,
                mode='lines',
                fill='tonexty',
                line=dict(color=COLORS['primary'], width=3),
                fillcolor=f"rgba{tuple(list(bytes.fromhex(COLORS['primary'][1:])) + [0.3])}",
                name='Elevación',
                hovertemplate='Distancia: %{x:.2f}km<br>' +
                              'Elevación: %{y:.1f}m<extra></extra>'
            ))

            # Agregar marcadores de sectores
            sectors = track_data.get('sectors', [])
            for sector in sectors:
                start_pos = sector['start'] / len(z_coords) * circuit_info.get('length', len(z_coords))
                fig.add_vline(
                    x=start_pos,
                    line_dash="dash",
                    line_color=sector.get('color', '#CCCCCC'),
                    annotation_text=sector['name']
                )

            fig.update_layout(
                title=f"Perfil de Elevación - {circuit_info.get('circuitName', 'Circuito')}",
                xaxis_title='Distancia (km)',
                yaxis_title='Elevación (m)',
                height=300,
                margin=dict(l=50, r=20, t=50, b=50),
                showlegend=False
            )

            return fig

        except Exception as e:
            logger.error(f"Error creando perfil de elevación: {e}")
            return go.Figure()


# Instancia global del componente
track_3d_component = Track3DComponent()