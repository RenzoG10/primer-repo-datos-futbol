import tweepy as tw
import schedule as horario
from dotenv import load_dotenv
import os

from funciones import *

dia, mes, anio, fecha, paisbuscadoarreglado, uservivo = inputs()

# Iniciar Selenium y BeautifulSoup
driver, url, html, soup, grupos = selenium(fecha)

ligas_y_partidos = buscar_partido(grupos)

partidosenvivo, partidosnojugados, partidosfinalizados = filtrado_partidos_vivo_nojugados_finalizados(ligas_y_partidos, paisbuscadoarreglado)

partidos(dia, mes, anio, uservivo, partidosenvivo, partidosnojugados, partidosfinalizados, driver)


# las credenciales para que se asocie la account, utilizo el .env porque es mas seguro a la hora de subir a repositorios

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# cuerpo

client = tw.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

# Mostrar resultados
partidosenvivo = []
partidosnoenvivo = []
partidosfinalizados = []

def generar_mensaje2(ligas_y_partidos):
    mensaje = ""

    partidosenvivo, partidosnojugados, partidosfinalizados = filtrado_partidos_vivo_nojugados_finalizados(ligas_y_partidos, paisbuscadoarreglado)

    if uservivo == "VIVO":
        mensaje = ("Partidos en vivo:")
        for liga, minutos, equipo1, resultado, equipo2 in partidosenvivo:
            mensaje += (f"\n{liga}\n{minutos:<5} {equipo1} {resultado} {equipo2}")
    
    elif uservivo == "SEGUIMIENTO":
        mensaje = ("Partidos en vivo:")
        ligas = {}
        for liga, minutos, equipo1, resultado, equipo2 in partidosenvivo:
            if liga not in ligas:
                ligas[liga] = []
            ligas[liga].append(f"{minutos:<20} {equipo1:<30} {resultado:<20} {equipo2:<30}")

        for liga, lista_partidos in ligas.items():
            mensaje += (f"\nLiga: {liga}\n")
            for partido in lista_partidos:
                mensaje += (partido)

            estado_previos = {}

        print("\nMonitoreando cambios en los resultados. Presione Ctrl+C para detener.\n")

        try:
            while True:
                estado_actual = {}

                # Aquí deberías volver a obtener la página y analizar los datos dinámicamente
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Extraer los datos de los partidos
                partidos = soup.find_all('a', class_="css-s4hjf6-MatchWrapper e1ek4pst2")

                for partido in partidos:
                    equipos1_div = partido.find("div", class_="css-9871a0-StatusAndHomeTeamWrapper e1ek4pst4")
                    equipos2_div = partido.find("div", class_="css-gn249o-AwayTeamAndFollowWrapper e1ek4pst5")
                    resultados_div = partido.find("div", class_="css-1wgtcp0-LSMatchScoreAndRedCardsContainer e5pc0pz6")
                    minutos_div = partido.find("span", class_="css-doevad-StatusDotCSS e1yf8uo31")

                    equipo1 = equipos1_div.text.strip() if equipos1_div else "Equipo no encontrado"
                    equipo2 = equipos2_div.text.strip() if equipos2_div else "Equipo no encontrado"
                    resultado = resultados_div.text.strip() if resultados_div else "0 - 0"
                    minutos = minutos_div.text.strip() if minutos_div else ""

                    # Asegúrate de limpiar minutos de los nombres de los equipos
                    equipo1 = equipo1.replace(minutos, "").strip()
                    equipo2 = equipo2.replace(minutos, "").strip()

                    # Verificar si el partido ya estaba en estado_previos
                    if (equipo1, equipo2) in estado_previos:
                        resultado_anterior, minutos_anterior = estado_previos[(equipo1, equipo2)]

                        # Detectar goles
                        if resultado_anterior != resultado:
                            mesnaje = (f"{minutos} GOL en el partido {equipo1} vs {equipo2}! Nuevo resultado: {resultado}")

                        # Detectar inicio del partido
                        if minutos_anterior == "" and minutos != "":
                            mensaje = (f"{minutos} Comenzó el partido {equipo1} vs {equipo2} con marcador: {resultado}")
                        
                        elif minutos_anterior != "Pen" and minutos == "Pen":
                            mensaje = (f"Tanda de penales en el partido {equipo1} vs {equipo2}")
                        
                        elif minutos_anterior == "ET" and minutos != minutos_anterior:
                            mensaje = (f"{minutos} Comenzó el segundo tiempo {equipo1} vs {equipo2} con marcador: {resultado}")

                        elif minutos_anterior != "ET" and minutos == "ET":
                            mensaje = (f"Entre Tiempo en el partido {equipo1} vs {equipo2} con marcador: {resultado}")

                    else:
                        # Detectar nuevos partidos agregados al monitoreo
                        if minutos != "" and estado_previos != {}:
                            mensaje = (f"{minutos} Comenzó el partido {equipo1} vs {equipo2} con marcador: {resultado}")

                    # Actualizar estado actual
                    estado_actual[(equipo1, equipo2)] = (resultado, minutos)

                # Detectar partidos finalizados (presentes en estado_previos pero no en estado_actual)
                partidos_finalizados = set(estado_previos.keys()) - set(estado_actual.keys())
                for equipo1, equipo2 in partidos_finalizados:
                    resultado_final, _ = estado_previos[(equipo1, equipo2)]
                    mensaje = (f"Finalizó el partido {equipo1} vs {equipo2} con marcador: {resultado_final}")


                # Actualizar el estado previo para la próxima iteración
                estado_previos = estado_actual
                time.sleep(30)

        except KeyboardInterrupt:
            print("\nMonitoreo detenido por el usuario.")
        finally:
            driver.quit()

    elif uservivo == "NO JUGADOS":
        mensaje = ("Partidos sin jugar todavia:")
        for liga, minutos, equipo1, resultado, equipo2 in partidosnojugados:
            mensaje += (f"\n{minutos:<5} {equipo1} {resultado} {equipo2}")

    elif uservivo == "FINALIZADOS":
        mensaje = ("Partidos finalizados: ")
        for liga, minutos, equipo1, resultado, equipo2 in partidosfinalizados:
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