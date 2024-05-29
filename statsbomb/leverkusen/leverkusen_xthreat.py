# cargar librerías
import pandas as pd
import numpy as np
from statsbombpy import sb

# extraer los datos
competition_id = 9
season_id = 281

matches = sb.matches(competition_id = competition_id, season_id = season_id)

# hacer un loop para obtener todos los datos de la temporada
eventos_list = []

for match_id in matches["match_id"]:
    events = sb.events(match_id = match_id)
    events["match_id"] = match_id
    eventos_list.append(events)
df = pd.concat(eventos_list, ignore_index = True)

# filtrar para solo coger los pases completos del Bayer Leverkusen
df = df[df["team"] == "Bayer Leverkusen"]
df = df[df["type"] == "Pass"]
df = df[df["pass_outcome"] != "Incomplete"]
df = df[df["pass_outcome"] != "Out"]
df = df[df["pass_outcome"] != "Unknown"]
df = df[df["pass_outcome"] != "Pass Offside"]
df = df[df["pass_outcome"] != "Injury Clearance"]

# cargar la parrilla con los xT por zona
xT = pd.read_csv("../data/processed/xT_Grid.csv", header = None)
xT = np.array(xT)

xT_rows, xT_cols = xT.shape

# separar las coordenadas xy de la columna location y pass_end_location ya que en statsbomb estan juntas
df['x'] = df['location'].apply(lambda loc: loc[0])
df['y'] = df['location'].apply(lambda loc: loc[1])
df['endX'] = df['pass_end_location'].apply(lambda loc: loc[0])
df['endY'] = df['pass_end_location'].apply(lambda loc: loc[1])

# colocar las coordenadas dentro de cada celda de xT
df["x1_bin"] = pd.cut(df["x"], bins = xT_cols, labels = False)
df["y1_bin"] = pd.cut(df["y"], bins = xT_rows, labels = False)
df["x2_bin"] = pd.cut(df["endX"], bins = xT_cols, labels = False)
df["y2_bin"] = pd.cut(df["endY"], bins = xT_rows, labels = False)

# determinar el inicio y final de los pases
df["start_zone_value"] = df[["x1_bin", "y1_bin"]].apply(lambda x: xT[x[1]][x[0]], axis = 1)
df["end_zone_value"] = df[["x2_bin", "y2_bin"]].apply(lambda x: xT[x[1]][x[0]], axis = 1)

# sacar la diferencia para obtener el xT de cada pase
df["xT"] = df["end_zone_value"] - df["start_zone_value"]

# Ejemplo de uso para saber quien es el jugador con más xT por pase del Bayer Levekusen
df.groupby("player")["xT"].sum().sort_values(ascending = False)
