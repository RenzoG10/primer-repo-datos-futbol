from selenium import webdriver
from bs4 import BeautifulSoup

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
        return "TC"
    elif texto.endswith("Pen"):
        return "Pen"
    elif texto.endswith("AET"):
        return "AET"
    elif texto.endswith("ET"):
        return "ET"
    return None

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

    # Iniciar Selenium y BeautifulSoup
    driver = webdriver.Chrome(options=option)
    url = f"https://www.fotmob.com/es?date={fecha}"
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    grupos = soup.find_all('div', class_="css-1lleae-CardCSS e1mlfzv61")
    ligas_y_partidos = []

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

            resultados = None
            if div2 is not None:
                resultados = div2.find("div", class_="css-1wgtcp0-LSMatchScoreAndRedCardsContainer e5pc0pz6")

            if resultados is None:
                div4 = partido.find("div", class_="css-k083tz-StatusLSMatchWrapperCSS e5pc0pz0")
                if div4 is not None:
                    resultados = div4.find("span", class_="css-ky5j63-LSMatchStatusTime e5pc0pz3")
                if resultados is None:
                    resultados = "Hora no encontrada"

            equipo1 = equipos1_div1.text.strip() if equipos1_div1 else "Equipo no encontrado"
            resultado = resultados.text.strip() if hasattr(resultados, 'text') else resultados
            equipo2 = equipos2_div3.text.strip() if equipos2_div3 else "Equipo no encontrado"

            # Detectar minutos al final del nombre
            minutos = detectar_minutos(equipo1)
            estado = detectar_estado(equipo1)  # Detectar si es un TC, Pen, AET o ET

            # Eliminar los minutos y estado del nombre del equipo
            if minutos:
                equipo1 = equipo1.rstrip(minutos)
            if estado:
                equipo1 = equipo1.rstrip(estado)

            # Agregar los minutos y estado al lado de los minutos
            if estado:
                minutos = f"{minutos}{estado}"

            # Agregar el partido a la lista
            partidos_de_liga.append((minutos, equipo1, resultado, equipo2))

        ligas_y_partidos.append((titulo_liga, partidos_de_liga))

    # Mostrar resultados
    print(f"\nFecha: {dia}/{mes}/{anio}")
    for liga, partidos in ligas_y_partidos:
        if paisbuscadoarreglado == "Todos" or paisbuscadoarreglado == "Todo":
            print(f"\nLiga: {liga} - Total de partidos: {len(partidos)}\n")
            for minutos, equipo1, resultado, equipo2 in partidos:
                print(f"{minutos:<10} {equipo1:<30} {resultado:<20} {equipo2:<30}")
        elif paisbuscadoarreglado in liga:
            print(f"\nLiga: {liga} - Total de partidos: {len(partidos)}\n")
            for minutos, equipo1, resultado, equipo2 in partidos:
                print(f"{minutos:<10} {equipo1:<30} {resultado:<20} {equipo2:<30}")

# Ejecutar la función principal
buscar_partidos()
