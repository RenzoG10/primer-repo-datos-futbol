from selenium import webdriver
from bs4 import BeautifulSoup

option = webdriver.ChromeOptions()
option.add_argument("--headless")

print("\nIngrese fecha de partidos a buscar")
dia = input("Ingrese dia: ")
mes = input("Ingrese mes: ")
anio = input("Ingrese año: ")
fecha = str(anio)+str(mes).zfill(2)+str(dia).zfill(2)

paisbuscado = str(input("\nIngrese el pais de la liga a buscar: "))
paisbuscadoarreglado = paisbuscado.capitalize()

driver = webdriver.Chrome(options=option)
url = "https://www.fotmob.com/es?date="+fecha
driver.get(url)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

grupos = soup.find_all('div', class_="css-1lleae-CardCSS e1mlfzv61")

ligas_y_partidos = []

def detectar_minutos(texto):
    for car in texto: 
        if car.isalpha():
            texto.rstrip(car)

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
        
        detminutos = detectar_minutos(equipo1)
        if detminutos is None:
            minutos ="TC"
        else:
            minutos = detminutos
        equipo1 = equipo1.rstrip('TC')
        equipo2 = equipo2.rstrip('TC')

        partidos_de_liga.append((minutos, equipo1, resultado, equipo2))

    ligas_y_partidos.append((titulo_liga, partidos_de_liga))


print("\nFecha: ", dia+"/"+mes+"/"+anio)

for liga, partidos in ligas_y_partidos:
        
        if paisbuscadoarreglado == "Todos" or paisbuscadoarreglado == "Todo":
            print(f"\nLiga: {liga} - Total de partidos: {len(partidos)}\n")
            for minutos, equipo1, resultado, equipo2 in partidos:
                print(f"{minutos:<10} {equipo1:<30} {resultado:<20} {equipo2:<30}")

        elif paisbuscadoarreglado in liga:
            print(f"\nLiga: {liga} - Total de partidos: {len(partidos)}\n")
            for minutos, equipo1, resultado, equipo2 in partidos:
                print(f"{minutos:<10} {equipo1:<30} {resultado:<20} {equipo2:<30}")

# realizar validaciones en todos los inputs
# crear funciones para simplificar el codigo
# reordenar todo y comentar lo mas posible
# simplificar lineas con \n y eso