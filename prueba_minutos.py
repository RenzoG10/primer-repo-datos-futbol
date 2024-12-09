from selenium import webdriver
from bs4 import BeautifulSoup
import time 

# Configuración de Selenium
option = webdriver.ChromeOptions()
option.add_argument("--headless")


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

    for liga, partidos in ligas_y_partidos:
        if partidos:  # Mostrar solo ligas con partidos
            if paisbuscadoarreglado == "Todos" or paisbuscadoarreglado == "Todo" or paisbuscadoarreglado in liga:
                print(f"\nLiga: {liga} - Total de partidos: {len(partidos)}\n")
                for minutos, equipo1, resultado, equipo2 in partidos:
                    print(f"{minutos:<10} {equipo1:<30} {resultado:<20} {equipo2:<30}")

    #HACER LO DE LOS MINUTOS CON WEBSCRAPTING DIRECTAMENTE
    #NO HAY NADA HECHO