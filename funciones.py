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

    equipo_buscado = input("\nIngrese el nombre del equipo a buscar (o escriba 'Todos' o 'Todo' para buscar todo): ").strip()

    uservivo = input("\nIngrese VIVO o NO JUGADOS o FINALIZADOS: ")

    return dia,mes,anio, fecha, paisbuscadoarreglado, equipo_buscado, uservivo

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

def filtrado_equipos_liga(equipo_buscado, equipo1, equipo2, partidos_de_liga, minutos, resultado):
    
    partido_encontrado = False
    partidos_de_liga = []

    if equipo_buscado.lower() in equipo1.lower() or equipo_buscado.lower() in equipo2.lower():
        partidos_de_liga.append((minutos, equipo1, resultado, equipo2))
        partido_encontrado = True
    elif equipo_buscado.lower() == "todos" or equipo_buscado == "todo":
        partidos_de_liga.append((minutos, equipo1, resultado, equipo2))
        partido_encontrado = True

    return  partido_encontrado, partidos_de_liga

def buscar_partido(grupos, equipo_buscado):

    etiquetas_estado = ["TC", "Pen", "AET", "ET", "Ap", "Ab", "Ca"]

    ligas_y_partidos = []

    partido_encontrado = False

    # Extraer partidos
    for grupo in grupos:
        titulo_div = grupo.find('div', class_="css-170egrx-GroupTitle ei2uj7w0")
        titulo_liga = titulo_div.text.strip() if titulo_div else "Liga no encontrada"

        partidos = grupo.find_all('a', class_="css-s4hjf6-MatchWrapper e1ek4pst2")
        partidos_de_liga = []


        for partido in partidos:
            equipos1_div1 = partido.find("div", class_="css-9871a0-StatusAndHomeTeamWrapper e1ek4pst4")
            div2 = partido.find("div", class_="css-k083tz-StatusLSMatchWrapperCSS e5pc0pz0")
            equipos2_div3 = partido.find("div", class_="css-gn249o-AwayTeamAndFollowWrapper e1ek4pst5")
            minutos11 = equipos1_div1.find("span", class_ = "css-doevad-StatusDotCSS e1yf8uo31")

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

            # Agregar el partido a la lista si coincide con el equipo buscado o si se selecciona "Todos"
            partido_encontrado, partidos_de_liga = filtrado_equipos_liga(equipo_buscado, equipo1, equipo2, partidos_de_liga, minutos, resultado)
            
        ligas_y_partidos.append((titulo_liga, partidos_de_liga))
    
    return titulo_liga, minutos, equipo1, resultado, equipo2, partido_encontrado, ligas_y_partidos, partidos_de_liga

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
                            partidosenvivo.append((minutos, equipo1, resultado, equipo2))
                        elif minutos == "Partido Finalizado" or minutos == "Suspendido" or minutos == "Finalizo en Pen." or minutos == "Finalizado en T.E.":
                            partidosfinalizados.append((minutos, equipo1, resultado, equipo2))
                        elif minutos == "Cancelado" or minutos == "Aplazado":
                            partidosnojugados.append((minutos, equipo1, resultado, equipo2))
                    else:
                        partidosnojugados.append((minutos, equipo1, resultado, equipo2))

    return partidosenvivo, partidosnojugados, partidosfinalizados

def goles_comienzo(driver):
    # Almacén de estados previos
    estado_previos = {}

    print("Monitoreando cambios en los resultados. Presione Ctrl+C para detener.")

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
                    
                    if minutos_anterior == "Entre Tiempo" and minutos != minutos_anterior:
                        print(f"{minutos} Comenzó el segundo tiempo {equipo1} vs {equipo2} con marcador: {resultado}")

                    if minutos_anterior != "" and minutos == "Entre Tiempo":
                        print(f"{minutos} Entre Tiempo en el partido {equipo1} vs {equipo2} con marcador: {resultado}")

                    if minutos_anterior != "" and minutos in ["Partido Finalizado", "Finalizado en Pen.", "Finalizado en T.E."]:
                        print(f"{minutos} Finalizó el partido {equipo1} vs {equipo2} con marcador: {resultado}")

                else:
                    # Detectar nuevos partidos agregados al monitoreo
                    if minutos != "" and estado_previos != {}:
                        print(f"{minutos} Comenzó el partido {equipo1} vs {equipo2} con marcador: {resultado}")

                # Actualizar estado actual
                estado_actual[(equipo1, equipo2)] = (resultado, minutos)

            # Actualizar el estado previo para la próxima iteración
            estado_previos = estado_actual
            time.sleep(30)

    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
    finally:
        driver.quit()
