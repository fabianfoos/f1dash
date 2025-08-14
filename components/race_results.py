"""
Componente para mostrar resultados de carreras y clasificación
"""

import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional, Any
import logging

from config import COLORS

logger = logging.getLogger(__name__)


class RaceResultsComponent:
    """Componente para visualizar resultados de carreras"""

    def __init__(self):
        self.colors = COLORS

    def create_pole_position_card(self, qualifying_data: pd.DataFrame, race_info: Dict) -> dbc.Card:
        """
        Crea tarjeta destacada con información de pole position

        Args:
            qualifying_data: Datos de clasificación
            race_info: Información general de la carrera

        Returns:
            Card component con pole position
        """
        try:
            if qualifying_data.empty:
                return self._create_empty_pole_card()

            # Obtener pole position (primer lugar)
            pole_driver = qualifying_data.iloc[0] if len(qualifying_data) > 0 else None

            if pole_driver is None:
                return self._create_empty_pole_card()

            driver_name = f"{pole_driver.get('givenName', '')} {pole_driver.get('familyName', '')}"
            constructor_name = pole_driver.get('constructorName', 'N/A')
            pole_time = pole_driver.get('Q3', pole_driver.get('Q2', pole_driver.get('Q1', 'N/A')))

            # Crear imagen del piloto
            driver_image = self._get_driver_image(pole_driver.get('driverId', ''))
            constructor_logo = self._get_constructor_logo(pole_driver.get('constructorId', ''))

            card_content = dbc.Card([
                dbc.CardHeader([
                    html.H4("🏁 POLE POSITION", className="text-center mb-0",
                            style={'color': self.colors['primary'], 'font-weight': 'bold'})
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Img(
                                src=driver_image,
                                style={
                                    'width': '120px',
                                    'height': '120px',
                                    'border-radius': '50%',
                                    'object-fit': 'cover',
                                    'border': f'4px solid {self.colors["primary"]}'
                                },
                                className="mx-auto d-block"
                            )
                        ], width=12, className="text-center mb-3"),

                        dbc.Col([
                            html.H3(driver_name, className="text-center mb-2",
                                    style={'color': self.colors['text']}),

                            dbc.Badge(
                                constructor_name,
                                color="secondary",
                                className="d-block mx-auto mb-2",
                                style={'font-size': '0.9rem'}
                            ),

                            html.Div([
                                html.Img(src=constructor_logo, style={'width': '30px', 'height': '20px'}),
                                html.Span(f" {constructor_name}", style={'margin-left': '8px'})
                            ], className="text-center mb-3"),

                            html.Hr(),

                            html.Div([
                                html.Strong("Tiempo de Pole: ", style={'color': self.colors['text']}),
                                html.Span(pole_time, style={
                                    'font-size': '1.2rem',
                                    'font-weight': 'bold',
                                    'color': self.colors['primary']
                                })
                            ], className="text-center mb-2"),

                            html.Div([
                                html.Strong("Nacionalidad: "),
                                html.Span(pole_driver.get('driverNationality', 'N/A'))
                            ], className="text-center mb-2"),

                            html.Div([
                                html.Strong("Carrera: "),
                                html.Span(race_info.get('raceName', 'N/A'))
                            ], className="text-center")

                        ], width=12)
                    ])
                ])
            ], style={'border': f'2px solid {self.colors["primary"]}', 'box-shadow': '0 4px 8px rgba(0,0,0,0.1)'})

            return card_content

        except Exception as e:
            logger.error(f"Error creando tarjeta de pole position: {e}")
            return self._create_empty_pole_card()

    def create_results_table(self, race_results: Dict[str, Any]) -> dash_table.DataTable:
        """
        Crea tabla con resultados completos de la carrera

        Args:
            race_results: DataFrame con resultados de carrera

        Returns:
            DataTable component
        """
        try:
            if race_results.empty:
                return self._create_empty_results_table()

            # Preparar datos para la tabla
            table_data = []

            for _, result in race_results.iterrows():
                row_data = {
                    'Pos': result.get('position', 'N/A'),
                    'Piloto': f"{result.get('givenName', '')} {result.get('familyName', '')}",
                    'Escudería': result.get('constructorName', 'N/A'),
                    'Tiempo/Status': result.get('Time', {}).get('time', result.get('status', 'N/A')),
                    'Puntos': result.get('points', '0'),
                    'Vueltas': result.get('laps', 'N/A'),
                    'Parrilla': result.get('grid', 'N/A')
                }
                table_data.append(row_data)

            # Configurar columnas
            columns = [
                {'name': 'Pos', 'id': 'Pos', 'type': 'numeric'},
                {'name': 'Piloto', 'id': 'Piloto', 'type': 'text'},
                {'name': 'Escudería', 'id': 'Escudería', 'type': 'text'},
                {'name': 'Tiempo/Status', 'id': 'Tiempo/Status', 'type': 'text'},
                {'name': 'Puntos', 'id': 'Puntos', 'type': 'numeric'},
                {'name': 'Vueltas', 'id': 'Vueltas', 'type': 'numeric'},
                {'name': 'Parrilla', 'id': 'Parrilla', 'type': 'numeric'}
            ]

            return dash_table.DataTable(
                data=table_data,
                columns=columns,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'fontFamily': 'Arial',
                    'fontSize': '14px',
                    'padding': '10px'
                },
                style_header={
                    'backgroundColor': self.colors['primary'],
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 0},  # Primer lugar
                        'backgroundColor': '#FFD700',
                        'color': 'black',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'row_index': 1},  # Segundo lugar
                        'backgroundColor': '#C0C0C0',
                        'color': 'black',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'row_index': 2},  # Tercer lugar
                        'backgroundColor': '#CD7F32',
                        'color': 'white',
                        'fontWeight': 'bold'
                    }
                ],
                sort_action='native',
                filter_action='native',
                page_action='native',
                page_current=0,
                page_size=20
            )

        except Exception as e:
            logger.error(f"Error creando tabla de resultados: {e}")
            return self._create_empty_results_table()

    def create_qualifying_chart(self, qualifying_data: pd.DataFrame) -> go.Figure:
        """
        Crea gráfico de tiempos de clasificación

        Args:
            qualifying_data: Datos de clasificación

        Returns:
            Figure con gráfico de barras de tiempos
        """
        try:
            fig = go.Figure()

            if qualifying_data.empty:
                return self._create_empty_chart("Tiempos de Clasificación")

            # Preparar datos
            drivers = []
            times_q1 = []
            times_q2 = []
            times_q3 = []

            for _, row in qualifying_data.iterrows():
                driver_name = f"{row.get('givenName', '')} {row.get('familyName', '')}"
                drivers.append(driver_name)

                # Convertir tiempos a segundos para comparación
                times_q1.append(row.get('Q1', '').total_seconds())
                times_q2.append(row.get('Q2', '').total_seconds())
                times_q3.append(row.get('Q3', '').total_seconds())

            # Crear gráfico de barras
            if times_q3 and any(t > 0 for t in times_q3):
                fig.add_trace(go.Bar(
                    x=drivers[:10],  # Solo top 10
                    y=[t for t in times_q3[:10] if t > 0],
                    name='Q3',
                    marker_color=self.colors['primary'],
                    hovertemplate='<b>%{x}</b><br>Q3: %{text}<extra></extra>',
                    text=[self._seconds_to_time(t) for t in times_q3[:10] if t > 0]
                ))

            if times_q2 and any(t > 0 for t in times_q2):
                fig.add_trace(go.Bar(
                    x=drivers[10:15] if len(drivers) > 10 else [],
                    y=[t for t in times_q2[10:15] if t > 0] if len(times_q2) > 10 else [],
                    name='Q2',
                    marker_color=self.colors['accent'],
                    hovertemplate='<b>%{x}</b><br>Q2: %{text}<extra></extra>',
                    text=[self._seconds_to_time(t) for t in times_q2[10:15] if t > 0] if len(times_q2) > 10 else []
                ))

            if times_q1 and any(t > 0 for t in times_q1):
                fig.add_trace(go.Bar(
                    x=drivers[15:] if len(drivers) > 15 else [],
                    y=[t for t in times_q1[15:] if t > 0] if len(times_q1) > 15 else [],
                    name='Q1',
                    marker_color=self.colors['warning'],
                    hovertemplate='<b>%{x}</b><br>Q1: %{text}<extra></extra>',
                    text=[self._seconds_to_time(t) for t in times_q1[15:] if t > 0] if len(times_q1) > 15 else []
                ))

            fig.update_layout(
                title='Tiempos de Clasificación',
                xaxis_title='Pilotos',
                yaxis_title='Tiempo (segundos)',
                showlegend=True,
                height=400,
                margin=dict(l=50, r=50, t=50, b=100),
                xaxis={'categoryorder': 'total descending'}
            )

            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico de clasificación: {e}")
            return self._create_empty_chart("Tiempos de Clasificación")

    def create_drivers_grid(self, race_results: Dict[str, Any], qualifying_data: pd.DataFrame) -> html.Div:
        """
        Crea grilla visual con todos los pilotos

        Args:
            race_results: Resultados de carrera
            qualifying_data: Datos de clasificación

        Returns:
            Div component con grilla de pilotos
        """
        try:
            if race_results.empty:
                return html.Div("No hay datos de pilotos disponibles", className="text-center")

            cards = []

            for idx, result in race_results.iterrows():
                driver_name = f"{result.get('givenName', '')} {result.get('familyName', '')}"
                constructor_name = result.get('constructorName', 'N/A')
                position = result.get('position', 'N/A')
                points = result.get('points', '0')

                # Obtener tiempo de clasificación
                qualifying_time = 'N/A'
                if not qualifying_data.empty:
                    qual_row = qualifying_data[qualifying_data['driverId'] == result.get('driverId')]
                    if not qual_row.empty:
                        qual_result = qual_row.iloc[0]
                        qualifying_time = qual_result.get('Q3', qual_result.get('Q2', qual_result.get('Q1', 'N/A')))

                # Determinar color de posición
                position_color = self.colors['text']
                if position == '1':
                    position_color = '#FFD700'  # Oro
                elif position == '2':
                    position_color = '#C0C0C0'  # Plata
                elif position == '3':
                    position_color = '#CD7F32'  # Bronce

                driver_image = self._get_driver_image(result.get('driverId', ''))

                card = dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Img(
                                    src=driver_image,
                                    style={
                                        'width': '60px',
                                        'height': '60px',
                                        'border-radius': '50%',
                                        'object-fit': 'cover'
                                    },
                                    className="mb-2"
                                ),
                                html.H6(driver_name, className="card-title", style={'font-size': '0.9rem'}),
                                html.P(constructor_name, className="card-text text-muted",
                                       style={'font-size': '0.8rem', 'margin-bottom': '5px'}),

                                dbc.Row([
                                    dbc.Col([
                                        html.Strong("Pos:", style={'font-size': '0.8rem'}),
                                        html.Span(f" {position}", style={
                                            'color': position_color,
                                            'font-weight': 'bold',
                                            'font-size': '0.9rem'
                                        })
                                    ], width=6),
                                    dbc.Col([
                                        html.Strong("Pts:", style={'font-size': '0.8rem'}),
                                        html.Span(f" {points}", style={'font-size': '0.9rem'})
                                    ], width=6)
                                ], className="mb-1"),

                                html.Small(f"Clasificación: {qualifying_time}",
                                           className="text-muted d-block",
                                           style={'font-size': '0.7rem'})
                            ], className="text-center")
                        ], style={'padding': '10px'})
                    ], style={'height': '200px', 'margin-bottom': '15px'})
                ], width=6, md=4, lg=3)

                cards.append(card)

            return html.Div([
                html.H4("Todos los Pilotos", className="mb-3"),
                dbc.Row(cards)
            ])

        except Exception as e:
            logger.error(f"Error creando grilla de pilotos: {e}")
            return html.Div("Error cargando datos de pilotos", className="text-center")
        
    def create_driver_positions_lines(self, race_data) -> go.Figure:
        if race_data.empty:
            return self._create_empty_chart("Posiciones de Pilotos")

        fig = px.line(
            x = race_data['LapNumber'],
            y = race_data['Position'],
            color = race_data['Driver'],
            labels = {
                'x': 'Número de Vuelta',
                'y': 'Posición',
                'color': 'Piloto'
            },
            text=None  # No mostrar etiquetas por defecto
        )
        # Invertir el eje Y para que la posición 1 esté arriba
        fig.update_yaxes(autorange='reversed')
        fig.update_layout(showlegend=False)

        # Ocultar las etiquetas de px.line (por si acaso)
        fig.update_traces(text=None, selector=dict(mode='lines+markers'))

        # Agregar etiquetas al final de cada línea
        for driver in race_data['Driver'].unique():
            driver_data = race_data[race_data['Driver'] == driver]
            
            if not driver_data.empty:
                last_lap = driver_data['LapNumber'].max()
                last_point = driver_data[driver_data['LapNumber'] == last_lap]
                fig.add_scatter(
                    x=last_point['LapNumber'],
                    y=last_point['Position'],
                    mode='text',
                    text=[driver],
                    textposition='middle right',
                    showlegend=False,
                    textfont=dict(size=12, color='black'),
                    hoverinfo='skip'
                )
        return fig

    def _seconds_to_time(self, seconds: float) -> str:
        """Convierte segundos a formato MM:SS.mmm"""
        try:
            if seconds <= 0:
                return 'N/A'

            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}:{remaining_seconds:06.3f}"

        except:
            return 'N/A'

    def _get_driver_image(self, driver_id: str) -> str:
        """Obtiene URL de imagen del piloto"""
        # En un entorno real, esto se conectaría a una base de datos de imágenes
        return DEFAULT_IMAGES['driver']

    def _get_constructor_logo(self, constructor_id: str) -> str:
        """Obtiene URL del logo de la escudería"""
        return DEFAULT_IMAGES['constructor']

    def _create_empty_pole_card(self) -> dbc.Card:
        """Crea tarjeta vacía de pole position"""
        return dbc.Card([
            dbc.CardHeader(
                html.H4("🏁 POLE POSITION", className="text-center mb-0")
            ),
            dbc.CardBody([
                html.Div("No hay datos de pole position disponibles",
                         className="text-center text-muted")
            ])
        ])

    def _create_empty_results_table(self) -> dash_table.DataTable:
        """Crea tabla vacía de resultados"""
        return dash_table.DataTable(
            data=[],
            columns=[
                {'name': 'Mensaje', 'id': 'mensaje'}
            ],
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': self.colors['text_light']}
        )

    def _create_empty_chart(self, title: str) -> go.Figure:
        """Crea gráfico vacío"""
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title='No hay datos disponibles',
            yaxis_title='',
            height=400
        )
        return fig


# Instancia global del componente
race_results_component = RaceResultsComponent()