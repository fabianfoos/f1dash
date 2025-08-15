"""
Aplicación principal del Dashboard F1 Interactivo
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import logging
from config import APP_CONFIG, COLORS
from utils.data_loader import F1DataLoader
from components.world_map import world_map_component
from components.track_3d import track_3d_component
from components.race_results import race_results_component
from components.season import season_component

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

years = F1DataLoader().load_seasons()

# Inicializar aplicación Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)
app.title = APP_CONFIG['title']

# ======================
#       LAYOUT
# ======================

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.I(className="fas fa-flag-checkered me-3", style={'color': COLORS['primary']}),
                    "F1 Dashboard Interactivo"
                ], className="text-center mb-0", style={'color': COLORS['text']}),
                html.P("Explora los circuitos, pilotos y resultados de Fórmula 1",
                       className="text-center text-muted")
            ], className="py-4")
        ], width=12)
    ]),

    # Controles de filtro
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Seleccionar Año:", className="form-label"),
                            dcc.Dropdown(
                                id='year-selector',
                                options=[{'label': str(year), 'value': year} for year in years],
                                value=years.max(),
                                clearable=False,
                                style={'color': COLORS['text']}
                            )
                        ], width=12),
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dcc.Graph(id='season-summary')
            ])
        ], width=12),
    ]),

    # Loading y almacenamiento de datos
    dcc.Loading(
        id="loading-data",
        type="default",
        children=[
            dcc.Store(id='circuits-data'),
            dcc.Store(id='races-data'),
            dcc.Store(id='selected-circuit-data'),
        ]
    ),

    # Contenido principal
    dbc.Row([
        # Mapa mundial
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="fas fa-globe me-2"),
                        "Mapa Mundial de Circuitos"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='world-map', config={'displayModeBar': True, 'displaylogo': False})
                ])
            ])
        ], width=12, lg=8),

        # Información de circuito
        dbc.Col([
            dbc.Row([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-info-circle me-2"),
                            "Información del Circuito"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([html.Div(id='circuit-info-panel')])
                ])
            ]),
        ], width=12, lg=4)
    ], className="mb-4"),

    # Sección detallada (3D + resultados)
    html.Div(id='detailed-section', style={'display': 'none'}, children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-cube me-2"),
                            "Vista del Circuito"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='track-3d', config={'displayModeBar': True, 'displaylogo': False})
                    ])
                ])
            ], width=12, lg=8),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-chart-line me-2"),
                            "Perfil de Elevación"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([dcc.Graph(id='elevation-profile')])
                ])
            ], width=12, lg=4)
        ], className="mb-4"),

        # Resultados
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-trophy me-2"),
                            "Resultados de Carreras"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Tabs(
                            id="results-tabs",
                            children=[
                                dbc.Tab(label="Pole Position", tab_id="pole"),
                                dbc.Tab(label="Resultados", tab_id="results"),
                                dbc.Tab(label="Clasificación", tab_id="qualifying"),
                                dbc.Tab(label="Todos los Pilotos", tab_id="drivers")
                            ],
                            active_tab="pole"
                        ),
                        html.Div(id="tab-content", className="mt-3")
                    ])
                ])
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H4([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Posiciones de los Pilotos"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='result-positions')
                    ])
                ])
            ], width=12)
        ])
    ]),

    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "Dashboard F1 Interactivo • ",
                html.A("Datos de Ergast API", href="http://ergast.com/mrd/", target="_blank"),
                " • Desarrollado con Dash & Plotly"
            ], className="text-center text-muted small")
        ], width=12)
    ], className="mt-5")
], fluid=True, className="px-4")


# ======================
#   CALLBACKS
# ======================

@app.callback(
    [Output('circuits-data', 'data'),
     Output('races-data', 'data'),
     Output('season-summary', 'figure')],
    [Input('year-selector', 'value')]
)
def load_initial_data(selected_year):
    try:
        loader = F1DataLoader()

        circuits_df = loader.load_circuits(selected_year)
        if circuits_df is None:
            circuits_df = pd.DataFrame()

        races_df = loader.load_races_by_year(selected_year)
        if races_df is None:
            races_df = pd.DataFrame()

        return circuits_df.to_dict('records'), races_df.to_dict('records'), season_component.create_season_summary(selected_year)
    except Exception as e:
        logger.error(f"Error cargando datos iniciales: {e}")
        return [], [], []


@app.callback(
    Output('world-map', 'figure'),
    [Input('circuits-data', 'data'),
     Input('races-data', 'data'),
     Input('year-selector', 'value')]
)
def update_world_map(circuits_data, races_data, selected_year):
    try:
        if not circuits_data:
            return world_map_component._create_empty_map()

        circuits_df = pd.DataFrame(circuits_data)
        races_df = pd.DataFrame(races_data) if races_data else pd.DataFrame()

        return world_map_component.create_circuits_map(circuits_df, races_df, selected_year)
    except Exception as e:
        logger.error(f"Error actualizando mapa mundial: {e}")
        return world_map_component._create_empty_map()


@app.callback(
    [Output('selected-circuit-data', 'data'),
     Output('circuit-info-panel', 'children'),
     Output('detailed-section', 'style')],
    [Input('world-map', 'clickData')],
    [State('circuits-data', 'data'),
     State('races-data', 'data')]
)
def handle_circuit_selection(click_data, circuits_data, races_data):
    try:
        if not click_data or not circuits_data:
            return {}, create_empty_circuit_info(), {'display': 'none'}

        point_data = click_data['points'][0]
        custom_data = point_data.get('customdata', [])
        if not custom_data or len(custom_data) < 3:
            return {}, create_empty_circuit_info(), {'display': 'none'}

        circuit_id = custom_data[0]
        circuits_df = pd.DataFrame(circuits_data)
        circuit_row = circuits_df[circuits_df['circuitId'] == circuit_id]
        if circuit_row.empty:
            return {}, create_empty_circuit_info(), {'display': 'none'}
        circuit_info = circuit_row.iloc[0].to_dict()

        races_info = []
        if races_data:
            races_df = pd.DataFrame(races_data)
            races_info = races_df[races_df['circuitId'] == circuit_id].to_dict('records')

        return {
            'circuit_info': circuit_info,
            'races_info': races_info,
            'circuit_id': circuit_id
        }, create_circuit_info_panel(circuit_info, races_info), {'display': 'block'}
    except Exception as e:
        logger.error(f"Error manejando selección de circuito: {e}")
        return {}, create_empty_circuit_info(), {'display': 'none'}


@app.callback(
    [Output('track-3d', 'figure'),
     Output('elevation-profile', 'figure'),
     Output('result-positions', 'figure')],
    [Input('selected-circuit-data', 'data')]
)
def update_3d_visualization(selected_circuit_data):
    try:
        if not selected_circuit_data or 'circuit_id' not in selected_circuit_data:
            return go.Figure(), go.Figure(), go.Figure()

        loader = F1DataLoader()
        track_data = loader.load_track_elevation_data(selected_circuit_data)
        fig_3d = track_3d_component.create_3d_track(track_data, selected_circuit_data['circuit_info'])
        fig_elev = track_3d_component.create_elevation_profile(track_data, selected_circuit_data)
        fig_positions = race_results_component.create_driver_positions_lines(loader.load_race_positions_laps(
            selected_circuit_data['races_info'][0]['season'],
            selected_circuit_data['races_info'][0]['round']
        ))

        return fig_3d, fig_elev, fig_positions
    except Exception as e:
        logger.error(f"Error actualizando visualización 3D: {e}")
        return go.Figure(), go.Figure(), go.Figure()


@app.callback(
    Output('tab-content', 'children'),
    [Input('results-tabs', 'active_tab'),
     Input('selected-circuit-data', 'data')],
    [State('year-selector', 'value')]
)
def update_results_content(active_tab, selected_circuit_data, selected_year):
    try:
        if not selected_circuit_data or 'races_info' not in selected_circuit_data:
            return html.Div("Selecciona un circuito para ver los resultados", className="text-center text-muted")

        races_info = selected_circuit_data['races_info']
        if not races_info:
            return html.Div("No hay datos de carreras disponibles para este circuito", className="text-center text-muted")

        race_info = races_info[0]
        round_num = race_info.get('round')

        loader = F1DataLoader()
        race_results = loader.load_race_results(selected_year, round_num)
        qualifying_data = loader.get_qualifying_results(selected_year, round_num)

        if active_tab == "pole":
            return race_results_component.create_pole_position_card(qualifying_data, race_info)
        elif active_tab == "results":
            return race_results_component.create_results_table(race_results)
        elif active_tab == "qualifying":
            return dcc.Graph(figure=race_results_component.create_qualifying_chart(qualifying_data), config={'displayModeBar': False})
        elif active_tab == "drivers":
            return race_results_component.create_drivers_grid(race_results, qualifying_data)

        return html.Div("Contenido no disponible")
    except Exception as e:
        logger.error(f"Error actualizando contenido de resultados: {e}")
        return html.Div("Error cargando datos de resultados", className="text-center text-muted")


def create_circuit_info_panel(circuit_info: dict, races_info: list) -> html.Div:
    try:
        circuit_name = circuit_info.get('circuitName', 'N/A')
        locality = circuit_info.get('locality', 'N/A')
        country = circuit_info.get('country', 'N/A')

        info_items = [
            html.H5(circuit_name, className="mb-3", style={'color': COLORS['primary']}),
            html.P([html.I(className="fas fa-map-marker-alt me-2"), f"{locality}, {country}"]),
            html.P([html.I(className="fas fa-link me-2"), html.A("Más información", href=circuit_info.get('url', '#'), target="_blank")])
        ]

        if races_info:
            info_items.append(html.Hr())
            info_items.append(html.H6("Carreras en este circuito:"))
            for race in races_info:
                info_items.append(html.P([html.I(className="fas fa-calendar me-2"), f"{race.get('raceName')} ({race.get('date')})"], className="small"))

        return html.Div(info_items)
    except Exception as e:
        logger.error(f"Error creando panel de información: {e}")
        return create_empty_circuit_info()


def create_empty_circuit_info() -> html.Div:
    return html.Div([
        html.I(className="fas fa-mouse-pointer fa-3x mb-3", style={'color': COLORS['text_light']}),
        html.P("Haz clic en un circuito del mapa para ver información detallada", className="text-muted text-center")
    ], className="text-center py-4")


if __name__ == '__main__':
    logger.info("Iniciando F1 Dashboard...")
    app.run(debug=APP_CONFIG['debug'], host=APP_CONFIG['host'], port=APP_CONFIG['port'])
