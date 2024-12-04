from selenium import webdriver
from bs4 import BeautifulSoup

# Configuración de Selenium
def configurar_driver():
    """Configura el driver de Selenium en modo headless."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

# Validación de inputs
def validar_fecha():
    
    #Valida el ingreso de una fecha válida
    while True:
        try:
            dia = int(input("Ingrese día (1-31): "))
            mes = int(input("Ingrese mes (1-12): "))
            anio = int(input("Ingrese año (ej. 2024): "))
            if 1 <= dia <= 31 and 1 <= mes <= 12 and anio > 0:
                return f"{anio}{str(mes).zfill(2)}{str(dia).zfill(2)}"
            else:
                print("Fecha inválida. Intente de nuevo.")
        except ValueError:
            print("Entrada no válida. Intente de nuevo.")

def validar_pais():

    #Valida el ingreso del país o permite seleccionar 'Todos'
    while True:
        pais = input("Ingrese el país de la liga a buscar (o 'Todos' para todas): ").strip()
        if pais:
            return pais.capitalize()
        print("Debe ingresar un país válido.")

# Extracción de datos
def extraer_partidos(soup):

    #Extrae los partidos y las ligas de la página parseada
    ligas_y_partidos = []
    grupos = soup.find_all('div', class_="css-1lleae-CardCSS e1mlfzv61")

    for grupo in grupos:

        # Título de la liga
        titulo_div = grupo.find('div', class_="css-170egrx-GroupTitle ei2uj7w0")
        titulo_liga = titulo_div.text.strip() if titulo_div else "Liga no encontrada"

        # Partidos de la liga
        partidos = grupo.find_all('a', class_="css-s4hjf6-MatchWrapper e1ek4pst2")
        partidos_de_liga = []

        for partido in partidos:
            equipo1, resultado, equipo2 = extraer_datos_partido(partido)
            partidos_de_liga.append((equipo1, resultado, equipo2))

        ligas_y_partidos.append((titulo_liga, partidos_de_liga))

    return ligas_y_partidos

def extraer_datos_partido(partido):

    #Extrae datos individuales de un partido
    equipos1_div1 = partido.find("div", class_="css-9871a0-StatusAndHomeTeamWrapper e1ek4pst4")
    div2 = partido.find("div", class_="css-k083tz-StatusLSMatchWrapperCSS e5pc0pz0") 
    equipos2_div3 = partido.find("div", class_="css-gn249o-AwayTeamAndFollowWrapper e1ek4pst5")

    # Resultado o estado del partido
    resultados = div2.find("div", class_="css-1wgtcp0-LSMatchScoreAndRedCardsContainer e5pc0pz6") if div2 else None
    if not resultados:
        resultados = div2.find("span", class_="css-ky5j63-LSMatchStatusTime e5pc0pz3") if div2 else "Hora no encontrada"

    # Equipos
    equipo1 = equipos1_div1.text.strip() if equipos1_div1 else "Equipo no encontrado"
    equipo2 = equipos2_div3.text.strip() if equipos2_div3 else "Equipo no encontrado"

    # Limpieza de datos
    equipo1 = equipo1.rstrip('TC')
    equipo2 = equipo2.rstrip('TC')
    resultado = resultados.text.strip() if hasattr(resultados, 'text') else resultados

    return equipo1, resultado, equipo2

# Presentación de resultados
def imprimir_resultados(ligas_y_partidos, paisbuscado):
    """Imprime los resultados filtrados por país o todos."""
    resultados_encontrados = False  # Bandera para comprobar si hay resultados

    print("\nResultados encontrados:\n")
    for liga, partidos in ligas_y_partidos:
        if paisbuscado in ("Todos", "Todo") or paisbuscado in liga:
            resultados_encontrados = True
            print(f"\nLiga: {liga} - Total de partidos: {len(partidos)}")
            for equipo1, resultado, equipo2 in partidos:
                print(f"{equipo1:<30} {resultado:<20} {equipo2:<30}")

    if not resultados_encontrados:
        print("No se encontraron ligas o partidos correspondientes al país ingresado.")

    print()

# Función principal
def main():
    print("\n⚽ Buscador de Partidos de Fútbol ⚽\n")
    fecha = validar_fecha()
    paisbuscado = validar_pais()

    driver = configurar_driver()
    url = f"https://www.fotmob.com/es?date={fecha}"
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    ligas_y_partidos = extraer_partidos(soup)
    imprimir_resultados(ligas_y_partidos, paisbuscado)

# Ejecutar el programa
if __name__ == "__main__":
    main()
