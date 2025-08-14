import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import fastf1


logger = logging.getLogger(__name__)

class F1DataLoader:
    def load_seasons(self):
        return fastf1.ergast.Ergast().get_seasons(limit=200)['season']
    
        # --- Métodos de carga ---
    def load_circuits(self, season: int):
        return fastf1.ergast.Ergast().get_circuits(season=season)

    def load_races_by_year(self, season: int):
        return fastf1.ergast.Ergast().get_race_schedule(season=season)

    def load_race_results(self, season: int, round_num: int) -> Optional[Dict[str, Any]]:
        return fastf1.ergast.Ergast().get_race_results(season=season, round=round_num).content[0]
    
    def load_race_positions_laps(self, season: int, round_num: int) -> pd.DataFrame:
        """Carga las posiciones de los pilotos por vuelta en una carrera específica."""
        # Cargar el evento y la sesión de carrera
        event = fastf1.get_event(season, round_num)
        session = event.get_session('R')  # Carrera
        session.load()

        # Obtener las posiciones por vuelta
        positions = session.laps[['Driver', 'LapNumber', 'Position']].copy()
        positions['LapNumber'] = positions['LapNumber'].astype(int)

        return positions

    # --- Métodos que faltaban ---
    def get_qualifying_results(self, season: int, round_num: int):
        return fastf1.ergast.Ergast().get_qualifying_results(season=season, round=round_num).content[0]

    def load_track_elevation_data(self, circuit):
        """Simulación temporal de datos de elevación"""
        #logger.warning("load_track_elevation_data: método simulado")
        #return {'distance': [0, 1, 2], 'elevation': [0, 5, 0]}

        # Descarga datos del evento
        event = fastf1.get_event(circuit['races_info'][0]['season'], circuit['circuit_id'])
        session = event.get_session('R')  # Carrera
        session.load()

        # Obtener datos de la pista
        track = session.laps.pick_fastest().telemetry

        # Coordenadas de la pista (x, y, z)
        x = track['X'].tolist()
        y = track['Y'].tolist()
        z = track['Z'].tolist() if 'Z' in track else [0]*len(x)  # Si no hay elevación, usar 0

        # Sectores
        #sectors = []
        #for i, sector in enumerate(track['SectorStart']):
        #    sectors.append({
        #        'name': f'Sector {i+1}',
        #        'start': sector,
        #        'end': track['SectorEnd'][i] if 'SectorEnd' in track else sector+1,
        #        'color': ['#00FF00', '#FFFF00', '#FF0000'][i]  # Opcional
        #    })
#
        ## Zonas DRS (si existen)
        #drs_zones = []
        #if hasattr(track, 'DRSZones'):
        #    for i, zone in enumerate(track.DRSZones):
        #        drs_zones.append({
        #            'name': f'DRS {i+1}',
        #            'start': zone['start'],
        #            'end': zone['end']
        #        })
#
        ## Curvas importantes (puedes definirlas manualmente o extraerlas si tienes info)
        #turns = []
        #if hasattr(track, 'Turns'):
        #    for turn in track.Turns:
        #        turns.append({
        #            'number': turn['number'],
        #            'position': turn['position'],
        #            'type': turn.get('type', 'normal'),
        #            'difficulty': turn.get('difficulty', 'medium')
        #        })
#
        # Diccionario final para tu componente
        return {
            'x': x,
            'y': y,
            'z': z,
        #    'sectors': sectors,
        #    'drs_zones': drs_zones,
        #    'turns': turns
        }


# --- Funciones wrapper ---
def get_circuits(season: int): return F1DataLoader().load_circuits(season)
def get_races_by_year(season: int): return F1DataLoader().load_races_by_year(season)
def get_race_results(season: int, round_num): return F1DataLoader().load_race_results(season, round_num)
