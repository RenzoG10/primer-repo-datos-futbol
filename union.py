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

def monitorear_y_twittear(driver):
    estado_previos = {}
    print("\nMonitoreando cambios en los resultados. Presione Ctrl+C para detener.\n")

    try:
        while True:
            estado_actual = {}

            # Obtener el HTML de la página actualizada
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

                estado_actual[(equipo1, equipo2)] = (resultado, minutos)

                # Verificar cambios
                if (equipo1, equipo2) in estado_previos:
                    resultado_anterior, minutos_anterior = estado_previos[(equipo1, equipo2)]

                    # Detectar gol
                    if resultado_anterior != resultado:
                        mensaje = f" ⚽¡GOL! en el partido:\n{equipo1} vs {equipo2}\nNuevo marcador: {resultado} ({minutos} minutos)"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                    # Detectar inicio del partido
                    if minutos_anterior == "" and minutos != "":
                        mensaje = f"Comenzó el partido:\n{equipo1} vs {equipo2}\nMarcador inicial: {resultado}"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                    # Detectar entretiempo
                    if minutos_anterior != "ET" and minutos == "ET":
                        mensaje = f"Entretiempo en el partido:\n{equipo1} vs {equipo2}\nMarcador: {resultado}"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                    if minutos_anterior == "ET" and minutos != "ET":
                        mensaje = f"Comenzo el segundo tiempo en {equipo1} vs {equipo2}\nMarcador: {resultado}"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                    # Detectar tanda de penales
                    if minutos_anterior != "Pen" and minutos == "Pen":
                        mensaje = f"Tanda de penales\n{equipo1} vs {equipo2}"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                else:
                    # Detectar nuevos partidos agregados
                    if minutos != "":
                        mensaje = f"Nuevo partido en seguimiento: {equipo1} vs {equipo2}\nMarcador: {resultado} ({minutos} minutos)"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

            # Detectar partidos finalizados
            partidos_finalizados = set(estado_previos.keys()) - set(estado_actual.keys())
            for equipo1, equipo2 in partidos_finalizados:
                resultado_final, _ = estado_previos[(equipo1, equipo2)]
                mensaje = f"Finalizó el partido: {equipo1} vs {equipo2}\nResultado final: {resultado_final}"
                client.create_tweet(text=mensaje)
                print(f"Tweet enviado: {mensaje}")

            # Actualizar estado previo
            estado_previos = estado_actual

            # Pausar antes de la próxima iteración
            
            time.sleep(30)

    except tw.TooManyRequests as e:
        print("Error: Demasiadas requests, pausa tactica de 15 min")
        time.sleep(2 * 60)  # Pausa de 15 minutos

    except Exception as e:
        print(f"Error al publicar el tweet: {e}")

    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")

    finally:
        driver.quit()

# Inicia el monitoreo
monitorear_y_twittear(driver)