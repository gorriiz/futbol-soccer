# caragar librerías
from statsbombpy import sb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from mplsoccer import Pitch
from sklearn.cluster import KMeans

#obtener los datos
competition_id = 9
season_id = 281

matches = sb.matches(competition_id = competition_id, season_id = season_id)

eventos_list = []

for match_id in matches["match_id"]:
    events = sb.events(match_id = match_id)
    events["match_id"] = match_id
    eventos_list.append(events)
df = pd.concat(eventos_list, ignore_index = True)

# filtrar el df con los datos que queremos
df = df[["team", "type", "location", "pass_end_location"]]

df = df[(df["team"] == "Bayer Leverkusen") & (df["type"] == "Pass")].reset_index()

# separar las coordenadas xy en location y en pass_end_location
df['x'] = df['location'].apply(lambda loc: loc[0])
df['y'] = df['location'].apply(lambda loc: loc[1])
df['endX'] = df['pass_end_location'].apply(lambda loc: loc[0])
df['endY'] = df['pass_end_location'].apply(lambda loc: loc[1])

df.drop(["location", "pass_end_location"], axis = 1, inplace = True)

# aplicar el modelo de clustering
X = np.array(df[["x", "y", "endX", "endY"]])
kmeans = KMeans(n_clusters = 100, random_state = 100) # uso n_clusters = 100 para que la cantidad de pases no sea enorme, ajustalo a la cantidad total de pases
kmeans.fit(X)
df["cluster"] = kmeans.predict(X)

#graficar los pases en el campo
fig, ax = plt.subplots(figsize = (10, 10))
fig.set_facecolor("w")
ax.patch.set_facecolor("w")
pitch = Pitch(pitch_type = "statsbomb", pitch_color = "w", line_color = "#7c7c7c")
pitch.draw(ax = ax)

for x in range(len(df["cluster"])):
    
    if df["cluster"][x] == 18: # grafico los cinco clusters más representados
        pitch.lines(xstart = df["x"][x], ystart = df["y"][x], xend = df["endX"][x], yend = df["endY"][x],
                    color = "#E15A82", lw = 2, zorder = 2, comet = True, ax = ax)
    if df["cluster"][x] == 60:
        pitch.lines(xstart = df["x"][x], ystart = df["y"][x], xend = df["endX"][x], yend = df["endY"][x],
                    color = "#EEA934", lw = 2, zorder = 2, comet = True, ax = ax)
    if df["cluster"][x] == 5:
        pitch.lines(xstart = df["x"][x], ystart = df["y"][x], xend = df["endX"][x], yend = df["endY"][x],
                    color = "#F1CA56", lw = 2, zorder = 2, comet = True, ax = ax)
    if df["cluster"][x] == 1:
        pitch.lines(xstart = df["x"][x], ystart = df["y"][x], xend = df["endX"][x], yend = df["endY"][x],
                    color = "#7FF7A8", lw = 2, zorder = 2, comet = True, ax = ax)
    if df["cluster"][x] == 69:
        pitch.lines(xstart = df["x"][x], ystart = df["y"][x], xend = df["endX"][x], yend = df["endY"][x],
                    color = "#11C0A1", lw = 2, zorder = 2, comet = True, ax = ax)
