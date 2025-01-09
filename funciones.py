from selenium import webdriver
from bs4 import BeautifulSoup
import time 

def selenium(fecha):

    # Configuración de Selenium
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")

    driver = webdriver.Chrome(options=option)
    url = f"https://www.fotmob.com/es?date={fecha}"
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    grupos = soup.find_all('div', class_="css-1lleae-CardCSS e1mlfzv61")

    return driver, url, html, soup, grupos

def inputs():
    print("\nIngrese fecha de partidos a buscar")
    dia = input("Ingrese día: ")
    mes = input("Ingrese mes: ")
    anio = input("Ingrese año: ")
    fecha = str(anio) + str(mes).zfill(2) + str(dia).zfill(2)

    paisbuscado = str(input("\nIngrese el país de la liga a buscar: "))
    paisbuscadoarreglado = paisbuscado.capitalize()

    uservivo = input("\nIngrese VIVO o NO JUGADOS o FINALIZADOS: ")

    return dia,mes,anio, fecha, paisbuscadoarreglado, uservivo

# Función para detectar los minutos al final del texto (minutos)
def detectar_minutos(texto):
    """
    Extrae los números al final del texto, si los hay, y los retorna.
    """
    numeros = ""
    for car in reversed(texto):  # Recorre el texto desde el final
        if car.isdigit():  # Si es un número, lo agrega a los minutos
            numeros = car + numeros
        else:
            break  # Sale del bucle si no es un número

    return numeros

# Función para detectar si hay TC, Pen, AET o ET al final del nombre del equipo
def detectar_estado(texto):
    """
    Detecta si el nombre del equipo tiene TC, Pen, AET o ET al final.
    """
    if texto.endswith("TC"):
        return "Partido Finalizado"
    elif texto.endswith("Pen"):
        return "Finalizo en Pen."
    elif texto.endswith("AET"):
        return "Finalizado en T.E."
    elif texto.endswith("ET"):
        return "Entre Tiempo"
    elif texto.endswith("Ap"):
        return "Aplazado"
    elif texto.endswith("Ab"):
        return "Suspendido"
    elif texto.endswith("Ca"):
        return "Cancelado"

    return None

def limpiar_nombre_equipo(nombre, etiquetas):
    """
    Limpia el nombre del equipo eliminando etiquetas específicas al final.
    """
    for etiqueta in etiquetas:
        if nombre.endswith(etiqueta):
            nombre = nombre[: -len(etiqueta)].strip()  # Elimina la etiqueta y cualquier espacio adicional

    return nombre

def filtrado_partidos_vivo_nojugados_finalizados(ligas_y_partidos, paisbuscadoarreglado):

    partidosenvivo = []
    partidosnojugados = []
    partidosfinalizados = []

    for liga, partidos in ligas_y_partidos:
        if partidos:  # Mostrar solo ligas con partidos
            if paisbuscadoarreglado == "Todos" or paisbuscadoarreglado == "Todo" or paisbuscadoarreglado in liga:
                #print(f"\nLiga: {liga} - Total de partidos: {len(partidos)}\n")
                for minutos, equipo1, resultado, equipo2 in partidos:
                    #print(f"{minutos:<10} {equipo1:<30} {resultado:<20} {equipo2:<30}")
                    if minutos != "":
                        if minutos != "Partido Finalizado" and minutos != "Finalizo en Pen." and minutos != "Finalizado en T.E." and minutos != "Aplazado" and minutos != "Cancelado" and minutos != "Suspendido":
                            partidosenvivo.append((liga, minutos, equipo1, resultado, equipo2))
                        elif minutos == "Partido Finalizado" or minutos == "Suspendido" or minutos == "Finalizo en Pen." or minutos == "Finalizado en T.E.":
                            partidosfinalizados.append((liga, minutos, equipo1, resultado, equipo2))
                        elif minutos == "Cancelado" or minutos == "Aplazado":
                            partidosnojugados.append((liga, minutos, equipo1, resultado, equipo2))
                    else:
                        partidosnojugados.append((liga, minutos, equipo1, resultado, equipo2))

    return partidosenvivo, partidosnojugados, partidosfinalizados

def buscar_partido(grupos):
    etiquetas_estado = ["TC", "Pen", "AET", "ET", "Ap", "Ab", "Ca"]

    ligas_y_partidos = []

    # Extraer partidos
    for grupo in grupos:
        titulo_div = grupo.find('div', class_="css-170egrx-GroupTitle effkplk0")
        titulo_liga = titulo_div.text.strip() if titulo_div else "Liga no encontrada"

        partidos = grupo.find_all('a', class_="css-s4hjf6-MatchWrapper e1ek4pst2")
        partidos_de_liga = []

        for partido in partidos:
            equipos1_div1 = partido.find("div", class_="css-9871a0-StatusAndHomeTeamWrapper e1ek4pst4")
            div2 = partido.find("div", class_="css-k083tz-StatusLSMatchWrapperCSS e5pc0pz0")
            equipos2_div3 = partido.find("div", class_="css-gn249o-AwayTeamAndFollowWrapper e1ek4pst5")
            minutos11 = equipos1_div1.find("span", class_="css-doevad-StatusDotCSS e1yf8uo31")

            resultados = None
            if div2 is not None:
                resultados = div2.find("div", class_="css-1wgtcp0-LSMatchScoreAndRedCardsContainer e5pc0pz6")

            if resultados is None:
                div4 = partido.find("div", class_="css-k083tz-StatusLSMatchWrapperCSS e5pc0pz0")
                if div4 is not None:
                    resultados = div4.find("span", class_="css-ky5j63-LSMatchStatusTime e5pc0pz3")
                if resultados is None:
                    resultados = "Hora no encontrada"

            minutos = minutos11.text.strip() if minutos11 else ""
            equipo1 = equipos1_div1.text.strip() if equipos1_div1 else "Equipo no encontrado"
            resultado = resultados.text.strip() if hasattr(resultados, 'text') else resultados
            equipo2 = equipos2_div3.text.strip() if equipos2_div3 else "Equipo no encontrado"

            estado = detectar_estado(equipo1)  # Detectar si es un TC, Pen, AET o ET

            if estado is None:
                minutos = minutos
            else:
                minutos = estado

            # Eliminar los minutos y estado del nombre del equipo
            if minutos:
                equipo1 = equipo1.rstrip(minutos)
            if estado:
                equipo1 = limpiar_nombre_equipo(equipo1, etiquetas_estado)
                equipo2 = limpiar_nombre_equipo(equipo2, etiquetas_estado)

            # Agregar todos los partidos sin condiciones
            partidos_de_liga.append((minutos, equipo1, resultado, equipo2))
            
        ligas_y_partidos.append((titulo_liga, partidos_de_liga))

    return ligas_y_partidos

def goles_comienzo(driver):
    # Almacén de estados previos
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
                        print(f"{minutos} GOL en el partido {equipo1} vs {equipo2}! Nuevo resultado: {resultado}")

                    # Detectar inicio del partido
                    if minutos_anterior == "" and minutos != "":
                        print(f"{minutos} Comenzó el partido {equipo1} vs {equipo2} con marcador: {resultado}")
                    
                    elif minutos_anterior != "Pen" and minutos == "Pen":
                        print(f"Tanda de penales en el partido {equipo1} vs {equipo2}")
                    
                    elif minutos_anterior == "ET" and minutos != minutos_anterior:
                        print(f"{minutos} Comenzó el segundo tiempo {equipo1} vs {equipo2} con marcador: {resultado}")

                    elif minutos_anterior != "ET" and minutos == "ET":
                        print(f"Entre Tiempo en el partido {equipo1} vs {equipo2} con marcador: {resultado}")

                else:
                    # Detectar nuevos partidos agregados al monitoreo
                    if minutos != "" and estado_previos != {}:
                        print(f"{minutos} Comenzó el partido {equipo1} vs {equipo2} con marcador: {resultado}")

                # Actualizar estado actual
                estado_actual[(equipo1, equipo2)] = (resultado, minutos)

            # Detectar partidos finalizados (presentes en estado_previos pero no en estado_actual)
            partidos_finalizados = set(estado_previos.keys()) - set(estado_actual.keys())
            for equipo1, equipo2 in partidos_finalizados:
                resultado_final, _ = estado_previos[(equipo1, equipo2)]
                print(f"Finalizó el partido {equipo1} vs {equipo2} con marcador: {resultado_final}")


            # Actualizar el estado previo para la próxima iteración
            estado_previos = estado_actual
            time.sleep(30)

    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
    finally:
        driver.quit()

def partidos(dia, mes, anio, uservivo, partidosenvivo, partidosnojugados, partidosfinalizados, driver):

    # Mostrar resultados
    print(f"\nFecha: {dia}/{mes}/{anio}")

    if uservivo == "VIVO":
        print("Partidos en vivo:")
        ligas = {}
        for liga, minutos, equipo1, resultado, equipo2 in partidosenvivo:
            if liga not in ligas:
                ligas[liga] = []
            ligas[liga].append(f"{minutos:<20} {equipo1:<30} {resultado:<20} {equipo2:<30}")

        for liga, lista_partidos in ligas.items():
            print(f"\nLiga: {liga}\n")
            for partido in lista_partidos:
                print(partido)

        goles_comienzo(driver)

    elif uservivo == "NO JUGADOS":
        print("Partidos sin jugar todavía:")
        ligas = {}
        for liga, minutos, equipo1, resultado, equipo2 in partidosnojugados:
            if liga not in ligas:
                ligas[liga] = []
            ligas[liga].append(f"{minutos:<20} {equipo1:<30} {resultado:<20} {equipo2:<30}")

        for liga, lista_partidos in ligas.items():
            print(f"\nLiga: {liga}\n")
            for partido in lista_partidos:
                print(partido)

    elif uservivo == "FINALIZADOS":
        print("Partidos finalizados:")
        ligas = {}
        for liga, minutos, equipo1, resultado, equipo2 in partidosfinalizados:
            if liga not in ligas:
                ligas[liga] = []
            ligas[liga].append(f"{minutos:<20} {equipo1:<30} {resultado:<20} {equipo2:<30}")

        for liga, lista_partidos in ligas.items():
            print(f"\nLiga: {liga}\n")
            for partido in lista_partidos:
                print(partido)

def monitorear_y_twittear(driver, client, tw):

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
                    elif minutos_anterior != "ET" and minutos == "ET":
                        mensaje = f"Entretiempo en el partido:\n{equipo1} vs {equipo2}\nMarcador: {resultado}"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                    elif minutos_anterior == "ET" and minutos != "ET":
                        mensaje = f"Comenzo el segundo tiempo en {equipo1} vs {equipo2}\nMarcador: {resultado}"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                    # Detectar tanda de penales
                    elif minutos_anterior != "Pen" and minutos == "Pen":
                        mensaje = f"Tanda de penales\n{equipo1} vs {equipo2}"
                        client.create_tweet(text=mensaje)
                        print(f"Tweet enviado: {mensaje}")

                elif minutos != "":
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