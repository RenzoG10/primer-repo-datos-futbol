import tweepy as tw
import schedule as horario
from dotenv import load_dotenv
import os

from funciones import *

dia,mes,anio, fecha, paisbuscadoarreglado, uservivo = inputs()

driver, url, html, soup, grupos = selenium(fecha)

ligas_y_partidos = buscar_partido(grupos)

# las credenciales para que se asocie la account, utilizo el .env porque es mas seguro a la hora de subir a repositorios

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# cuerpo

client = tw.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

nombre_liga = ligas_y_partidos[0]

# Mostrar resultados
partidosenvivo = []
partidosnoenvivo = []
partidosfinalizados = []

def generar_mensaje2(ligas_y_partidos):
    mensaje = ""

    # Mostrar resultados
    #print(f"\nFecha: {dia}/{mes}/{anio}")
    '''if not partido_encontrado:
        mensaje = (f"No juega {equipo_buscado} en esta Fecha")'''

    partidosenvivo, partidosnojugados, partidosfinalizados = filtrado_partidos_vivo_nojugados_finalizados(ligas_y_partidos, paisbuscadoarreglado)

    if uservivo == "VIVO":
        #mensaje = ("Partidos en vivo:")
        for liga, minutos, equipo1, resultado, equipo2 in partidosenvivo:
            #mensaje += (f"\n{minutos:<5} {equipo1} {resultado} {equipo2}")
            if minutos == "Pen":
                mensaje = ("HAY PENALES EN:")
                mensaje += (f"\n {equipo1} {resultado} {equipo2}")


    elif uservivo == "NO JUGADOS":
        mensaje = ("Partidos sin jugar todavia:")
        for minutos, equipo1, resultado, equipo2 in partidosnojugados:
            mensaje += (f"\n{minutos:<5} {equipo1} {resultado} {equipo2}")

    elif uservivo == "FINALIZADOS":
        mensaje = ("Partidos finalizados: ")
        for minutos, equipo1, resultado, equipo2 in partidosfinalizados:
            mensaje += (f"\n{minutos:<5} {equipo1} {resultado} {equipo2}")

    #goles_comienzo(equipo1, equipo2, resultado, minutos, driver)
    return mensaje

# la funcion del twitteo 

def tweet():

    # para que no se repita el tweet (only testeo)

    texto = generar_mensaje2(ligas_y_partidos)

    # uso del try y except para que aunque haya un error siga corriendo el programa

    try:
        client.create_tweet(text=texto)
        print("Tweet publicado satisfactoriamente")
    except tw.TooManyRequests as e:
        print("Error: Demasiadas requests, pausa tactica de 15 min")
        time.sleep(2 * 60)  # Pausa de 15 minutos

    except Exception as e:
        print(f"Error al publicar el tweet: {e}")

# el timeset, es de prueba nomas, la idea es que el timeet este dentro de una funcion

horario.every(10).seconds.do(tweet) 

# el while para que se mantenga activo

print("Sigue funcionando")

while True:
    horario.run_pending() # verifica que no haya algo pendiente
    time.sleep(1) #crtl + c y frena el programa
