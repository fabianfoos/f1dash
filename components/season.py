import pandas as pd
import plotly.graph_objects as go
from plotly.io import show
from plotly.subplots import make_subplots

import fastf1 as ff1
from fastf1 import plotting

class SeasonComponent:
    def create_season_summary(self, season) -> go.Figure:
        schedule = ff1.get_event_schedule(season, include_testing=False)

        standings = []
        # Acorta los nombres de los eventos eliminando 'Grand Prix' del nombre.
        # Esto se usará para etiquetar nuestro gráfico.
        short_event_names = []

        # Filtra solo los eventos que ya han ocurrido
        schedule = schedule[schedule['EventDate'] < pd.to_datetime('today')]

        for _, event in schedule.iterrows():
            event_name, round_number = event["EventName"], event["RoundNumber"]
            short_event_names.append(event_name.replace("Grand Prix", "").strip())

            # Solo es necesario cargar los datos de resultados
            race = ff1.get_session(season, event_name, "R")
            race.load(laps=False, telemetry=False, weather=False, messages=False)

            # Añade puntos de la carrera sprint si aplica
            sprint = None
            # F1 ha usado diferentes nombres para el formato de evento sprint
            # Desde 2024 se llama "sprint_qualifying"
            # En 2023 debes buscar "sprint_shootout"
            # En 2022 y 2021 debes buscar "sprint"
            if event["EventFormat"] == "sprint_qualifying":
                sprint = ff1.get_session(season, event_name, "S")
                sprint.load(laps=False, telemetry=False, weather=False, messages=False)

            for _, driver_row in race.results.iterrows():
                abbreviation, race_points, race_position = (
                    driver_row["Abbreviation"],
                    driver_row["Points"],
                    driver_row["Position"],
                )

                sprint_points = 0
                if sprint is not None:
                    driver_row = sprint.results[
                        sprint.results["Abbreviation"] == abbreviation
                    ]
                    if not driver_row.empty:
                    # Necesitamos usar values[0] porque driver_row es realmente
                    # un dataframe con una sola fila
                        sprint_points = driver_row["Points"].values[0]

                standings.append(
                    {
                        "EventName": event_name,
                        "RoundNumber": round_number,
                        "Driver": abbreviation,
                        "DriverFullName": ff1.plotting.get_driver_name(abbreviation, race),
                        "Abbreviation": abbreviation,
                        "Points": race_points + sprint_points,
                        "Position": race_position,
                    }
                )

        df = pd.DataFrame(standings)

        heatmap_data = df.pivot(
            index="Driver", columns="RoundNumber", values="Points"
        ).fillna(0)

        # Guarda la clasificación final de pilotos y ordena los datos de modo que el piloto con menos puntos quede abajo
        heatmap_data["total_points"] = heatmap_data.sum(axis=1)
        heatmap_data = heatmap_data.sort_values(by="total_points", ascending=True)
        total_points = heatmap_data["total_points"].values
        heatmap_data = heatmap_data.drop(columns=["total_points"])

        # lo mismo para la posición.
        position_data = df.pivot(
            index="Driver", columns="RoundNumber", values="Position"
        ).fillna("N/A")

        hover_info = [
            [
                {
                    "position": position_data.at[driver, race],
                    "driver_full_name": df.loc[df["Driver"] == driver, "DriverFullName"].values[0],
                }
                for race in schedule["RoundNumber"]
            ]
            for driver in heatmap_data.index
        ]

        fig = make_subplots(
            rows=1,
            cols=2,
            column_widths=[0.85, 0.15],
            subplot_titles=("Resumen de Temporada", "Total de Puntos"),
        )
        fig.update_layout(width=900, height=800)

        # Mapa de calor resumen por carrera
        fig.add_trace(
            go.Heatmap(
                # Usa los nombres de las carreras como etiquetas en x y las abreviaturas de los pilotos en y
                x=short_event_names,
                y=heatmap_data.index,
                z=heatmap_data.values,
                # Usa los puntos obtenidos como hover
                text=heatmap_data.values,
                texttemplate="%{text}",
                textfont={"size": 12},
                customdata=hover_info,
                hovertemplate=(
                    "Piloto: %{customdata.driver_full_name}<br>"
                    "Carrera: %{x}<br>"
                    "Puntos: %{z}<br>"
                    "Posición: %{customdata.position}<extra></extra>"
                ),
                colorscale="YlGnBu",
                showscale=False,
                zmin=0,
                # Es necesario establecer zmax para los dos mapas de calor por separado ya que el valor máximo en el gráfico de puntos totales es mucho mayor.
                zmax=heatmap_data.values.max(),
            ),
            row=1,
            col=1,
        )

        # Mapa de calor para puntos totales
        fig.add_trace(
            go.Heatmap(
                x=["Total de Puntos"] * len(total_points),
                y=heatmap_data.index,
                z=total_points,
                text=total_points,
                texttemplate="%{text}",
                textfont={"size": 12},
                colorscale="YlGnBu",
                showscale=False,
                zmin=0,
                zmax=total_points.max(),
            ),
            row=1,
            col=2,
        )

        return fig

season_component = SeasonComponent()