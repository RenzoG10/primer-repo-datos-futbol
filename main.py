from selenium import webdriver
from bs4 import BeautifulSoup
import time 

# Configuración de Selenium
option = webdriver.ChromeOptions()
option.add_argument("--headless")

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

etiquetas_estado = ["TC", "Pen", "AET", "ET", "Ap", "Ab", "Ca"]

def limpiar_nombre_equipo(nombre, etiquetas):
    """
    Limpia el nombre del equipo eliminando etiquetas específicas al final.
    """
    for etiqueta in etiquetas:
        if nombre.endswith(etiqueta):
            nombre = nombre[: -len(etiqueta)].strip()  # Elimina la etiqueta y cualquier espacio adicional
    return nombre

# Función principal para buscar partidos
def buscar_partidos():
    # Solicitar fecha y país
    print("\nIngrese fecha de partidos a buscar")
    dia = input("Ingrese día: ")
    mes = input("Ingrese mes: ")
    anio = input("Ingrese año: ")
    fecha = str(anio) + str(mes).zfill(2) + str(dia).zfill(2)

    paisbuscado = str(input("\nIngrese el país de la liga a buscar: "))
    paisbuscadoarreglado = paisbuscado.capitalize()

    equipo_buscado = input("\nIngrese el nombre del equipo a buscar (o escriba 'Todos' o 'Todo' para buscar todo): ").strip()

    uservivo = input("\nIngrese VIVO o NO JUGADOS o FINALIZADOS: ")

    # Iniciar Selenium y BeautifulSoup
    driver = webdriver.Chrome(options=option)
    url = f"https://www.fotmob.com/es?date={fecha}"
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    grupos = soup.find_all('div', class_="css-1lleae-CardCSS e1mlfzv61")
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
            if equipo_buscado.lower() in equipo1.lower() or equipo_buscado.lower() in equipo2.lower():
                partidos_de_liga.append((minutos, equipo1, resultado, equipo2))
                partido_encontrado = True
            elif equipo_buscado.lower() == "todos" or equipo_buscado == "todo":
                partidos_de_liga.append((minutos, equipo1, resultado, equipo2))
                partido_encontrado = True
            
        ligas_y_partidos.append((titulo_liga, partidos_de_liga))

    # Mostrar resultados
    print(f"\nFecha: {dia}/{mes}/{anio}")
    if not partido_encontrado:
        print(f"No juega {equipo_buscado} en esta Fecha")
    
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
                        
    if uservivo == "VIVO":
        print("Partidos en vivo:")
        for minutos, equipo1, resultado, equipo2 in partidosenvivo:
            print(f"{minutos:<20} {equipo1:<30} {resultado:<20} {equipo2:<30}")
    
    # DETECCION DE GOLES Y DE COMIENZOS DE PARTIDOS

    # Almacén de estados previos
        estado_previos = {}

        print("Monitoreando cambios en los resultados. Presione Ctrl+C para detener.")

        try:
            while True:
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                grupos = soup.find_all('div', class_="css-1lleae-CardCSS e1mlfzv61")
                estado_actual = {}

                for grupo in grupos:
                    partidos = grupo.find_all('a', class_="css-s4hjf6-MatchWrapper e1ek4pst2")

                    for partido in partidos:
                        equipos1_div1 = partido.find("div", class_="css-9871a0-StatusAndHomeTeamWrapper e1ek4pst4")
                        div2 = partido.find("div", class_="css-k083tz-StatusLSMatchWrapperCSS e5pc0pz0")
                        equipos2_div3 = partido.find("div", class_="css-gn249o-AwayTeamAndFollowWrapper e1ek4pst5")

                        resultados = None
                        if div2:
                            resultados = div2.find("div", class_="css-1wgtcp0-LSMatchScoreAndRedCardsContainer e5pc0pz6")
                        if not resultados:
                            resultados = div2.find("span", class_="css-ky5j63-LSMatchStatusTime e5pc0pz3") if div2 else None

                        equipo1 = equipos1_div1.text.strip() if equipos1_div1 else "Equipo no encontrado"
                        equipo2 = equipos2_div3.text.strip() if equipos2_div3 else "Equipo no encontrado"
                        resultado = resultados.text.strip() if hasattr(resultados, 'text') else resultados

                        minutos = detectar_minutos(equipo1)

                        # Eliminar los minutos y estado del nombre del equipo
                        if minutos:
                            equipo1 = equipo1.rstrip(minutos)

                        if equipo1 and equipo2 and resultado:
                            key = f"{equipo1} vs {equipo2}"
                            estado_actual[key] = (resultado, minutos)

                            if key in estado_previos:
                                resultado_anterior, minutos_anteriores = estado_previos[key]

                                if minutos_anteriores == "" and minutos != "":
                                    print(f"{minutos} Comenzó el partido {key} con marcador: {resultado}")

                                # Detectar goles
                                if resultado_anterior != resultado:
                                    print(f"{minutos} GOL en el partido {key}! Nuevo resultado: {resultado}")

                            elif minutos == "1" or minutos == "0":
                                    print(f"{minutos} Comenzó el partido {key} con marcador: {resultado}")

                            
                            '''if key in estado_previos and (estado_previos[key] == "0 - 0" or estado_previos[key] == "") and (minutos == "1" or minutos == "0"):
                                print(f"{minutos} Comenzo el partido {key}!: Marcador: {resultado}")
                            
                            elif key in estado_previos and estado_previos[key] != resultado:
                                print(f"{minutos} GOL en el partido {key}! Nuevo resultado: {resultado}")'''


                estado_previos = estado_actual
                time.sleep(30)
        except KeyboardInterrupt:
            print("\nMonitoreo detenido por el usuario.")
        finally:
            driver.quit()

    elif uservivo == "NO JUGADOS":
        print("Partidos sin jugar todavia:")
        for minutos, equipo1, resultado, equipo2 in partidosnojugados:
            print(f"{minutos:<15} {equipo1:<30} {resultado:<20} {equipo2:<30}")

    elif uservivo == "FINALIZADOS":
        print("Partidos finalizados: ")
        for minutos, equipo1, resultado, equipo2 in partidosfinalizados:
            print(f"{minutos:<15} {equipo1:<30} {resultado:<20} {equipo2:<30}")



# Ejecutar la función principal
buscar_partidos()