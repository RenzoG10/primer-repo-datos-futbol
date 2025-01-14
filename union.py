import tweepy as tw
import schedule as horario
from dotenv import load_dotenv
import os

from funciones import *

dia, mes, anio, fecha, paisbuscadoarreglado, uservivo = inputs()

# Iniciar Selenium y BeautifulSoup
driver, url, html, soup, grupos = selenium(fecha)

ligas_y_partidos = buscar_partido(grupos)

#partidosenvivo, partidosnojugados, partidosfinalizados = filtrado_partidos_vivo_nojugados_finalizados(ligas_y_partidos, paisbuscadoarreglado)

# las credenciales para que se asocie la account, utilizo el .env porque es mas seguro a la hora de subir a repositorios

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# cuerpo

client = tw.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

driver, url, html, soup, grupos = selenium(fecha)

# Inicia el monitoreo
monitorear_y_twittear(driver, client, tw, grupos, paisbuscadoarreglado)