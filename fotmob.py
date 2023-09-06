import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from io import BytesIO
import urllib.request
from PIL import Image

def shotmap_fotmob(matchid):
    # recortar la url para que acepte la id del partido que escojamos
    url = "https://www.fotmob.com/match/" + str(matchid) + "/"
    # hacer la request a la api de FotMob
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    json_fotmob = json.loads(soup.find("script", attrs = {"id": "__NEXT_DATA__"}).contents[0])
    # buscar los datos que queremos incluir en el gráfico
    # estadísticas generales
    estadisticas_generales = json_fotmob["props"]["pageProps"]["general"]
    # colores de los equipos
    home_color = estadisticas_generales["teamColors"]["lightMode"]["home"]
    away_color = estadisticas_generales["teamColors"]["lightMode"]["away"]
    # nombre de los equipos
    home_team = estadisticas_generales["homeTeam"]
    away_team = estadisticas_generales["awayTeam"]
    # url de los escudos
    home_logo = json_fotmob["props"]["pageProps"]["header"]["teams"][0]["imageUrl"]
    away_logo = json_fotmob["props"]["pageProps"]["header"]["teams"][1]["imageUrl"]
    # goles marcados por cada equipò
    result_home = json_fotmob["props"]["pageProps"]["header"]["teams"][0]["score"]
    result_away = json_fotmob["props"]["pageProps"]["header"]["teams"][1]["score"]
    # hacemos un DataFrame con los disparos que nos proporcionan
    df_shots = pd.DataFrame(json_fotmob["props"]["pageProps"]["content"]["shotmap"]["shots"])
    # definir que equipo es el que realiza cada disparo
    team = []
    for t in df_shots["teamId"]:
        if t == home_team["id"]:
            team.append(home_team["name"])
        else:
            team.append(away_team["name"])
    
    # añadir la columna con el equipo que dispara    
    df_shots["team"] = team
    # creamos df filtrando el resultado de los disparos para que nos sea más fácil graficarlos
    # local: gol / no gol
    goal_h = df_shots[(df_shots["eventType"] == "Goal") & (df_shots["team"] == home_team["name"])]
    no_goal_h = df_shots[(df_shots["eventType"] != "Goal") & (df_shots["team"] == home_team["name"])]

    # visitante: gol / no gol
    goal_a = df_shots[(df_shots["eventType"] == "Goal") & (df_shots["team"] == away_team["name"])]
    no_goal_a = df_shots[(df_shots["eventType"] != "Goal") & (df_shots["team"] == away_team["name"])]
    
    # sacámos los goles esperados totales de cada equipo
    xg_home = df_shots[df_shots["teamId"] == home_team["id"]]["expectedGoals"].sum()
    xg_away = df_shots[df_shots["teamId"] == away_team["id"]]["expectedGoals"].sum()
    
    # empezamos a graficar el campo
    fig, ax = plt.subplots(figsize = (10, 5))
    pitch = Pitch(pitch_type = "custom", pitch_color = "#e0e1dd", pitch_length = 105, pitch_width = 68)
    pitch.draw(ax = ax)

    # graficamos los disparos
    # para los disparos del equipo local hay que transformar las coordenadas para que nos queden en la mitad de campo de la izquierda
    pitch.scatter(x = (goal_h["x"] - 105) * -1, y = (goal_h["y"] - 68) * -1, s = goal_h.expectedGoals * 700, c = home_color, ax = ax)
    pitch.scatter(x = (no_goal_h["x"] - 105) * -1, y = (no_goal_h["y"] - 68) * -1, s = no_goal_h.expectedGoals * 700,  c = home_color, alpha = 0.5, ax = ax)
    pitch.scatter(x = goal_a["x"], y = goal_a["y"], s = goal_a.expectedGoals * 700, c = away_color, ax = ax)
    pitch.scatter(x = no_goal_a["x"], y = no_goal_a["y"], s = no_goal_a.expectedGoals * 700, c = away_color, alpha = 0.5, ax = ax)
    
    # título y subtitulo con la información recogida anteriormente
    plt.title(str(result_home )+ " - " + str(result_away), x = 0.5, y = 0.77, fontsize = 20, weight = "bold")
    plt.text(51, 50, home_team["name"] + " (" + str(round(xg_home, 2)) + " xG)", ha = "right", weight = "bold")
    plt.text(53, 50, " (" + str(round(xg_away, 2)) + " xG) " + away_team["name"], ha = "left", weight = "bold")
    
    # añadimos los escudos    
    home_badge = fig.add_axes([0.388,0.70,0.1,0.1]) # badge
    home_badge.axis("off")
    url = home_logo
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    home_badge.imshow(img)
    
    away_badge = fig.add_axes([0.53,0.70,0.1,0.1]) # badge
    away_badge.axis("off")
    url = away_logo
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    away_badge.imshow(img)