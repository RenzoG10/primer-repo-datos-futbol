import tweepy as tw
import schedule as horario
from dotenv import load_dotenv
import time
import os

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

   # Detecta si el nombre del equipo tiene TC, Pen, AET o ET al final.
    if texto.endswith("TC"):
        return "Partido Finalizado"
    elif texto.endswith("Pen"):
        return "Tanda de penales"
    elif texto.endswith("AET"):
        return "Partido Finalizado"
    elif texto.endswith("ET"):
        return "Entre Tiempo"
    return None

# Solicitar fecha, país y equipo
print("\nIngrese fecha de partidos a buscar")
dia = input("Ingrese día: ")
mes = input("Ingrese mes: ")
anio = input("Ingrese año: ")
fecha = str(anio) + str(mes).zfill(2) + str(dia).zfill(2)

paisbuscado = str(input("\nIngrese el país de la liga a buscar: "))
paisbuscadoarreglado = paisbuscado.capitalize()

equipo_buscado = input("\nIngrese el nombre del equipo a buscar (o escriba 'Todos' o 'Todo' para buscar todo): ").strip()
uservivo = input("Ingrese VIVO o NO JUGADOS o FINALIZADOS: ")
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
        elif equipo_buscado.lower() == "todos" or equipo_buscado.lower() == "todo":
            partidos_de_liga.append((minutos, equipo1, resultado, equipo2))
            partido_encontrado = True
            
    ligas_y_partidos.append((titulo_liga, partidos_de_liga))

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
envivo = None # esta al pedo
parttermi = False # esta al pedo
partidosenvivo = []
partidosnoenvivo = []
partidosfinalizados = []

def generar_mensaje2(ligas_y_partidos):
    mensaje = ""
    if not partido_encontrado:
        mensaje = (f"No juega {equipo_buscado} en esta Fecha")
    for liga, partidos in ligas_y_partidos:
        if partidos:  # Mostrar solo ligas con partidos
            if paisbuscadoarreglado == "Todos" or paisbuscadoarreglado == "Todo" or paisbuscadoarreglado in liga:
                #mensaje = (f"\nLiga: {liga}\n")
                for minutos, equipo1, resultado, equipo2 in partidos:
                    #mensaje += (f"Tiempo en juego 🕒{minutos}\n{equipo1} {resultado} {equipo2}\n") #Hay que hacer mas condicionales para que printee bien si queremos todos los equipos
                    if minutos != "":
                        if minutos != "Partido Finalizado" and minutos != "Finalizo en tanda de Penales" and minutos != "Finalizado en Tiempo Extra":
                            envivo = True # esta al pedo
                            partidosenvivo.append((minutos, equipo1, resultado, equipo2))
                        elif minutos == "Partido Finalizado":
                            parttermi = True # esta al pedo
                            partidosfinalizados.append((minutos, equipo1, resultado, equipo2))
                        else:
                            envivo = False # esta al pedo
                            partidosnoenvivo.append((minutos, equipo1, resultado, equipo2))
       
    if uservivo == "VIVO":
        mensaje = ("Partidos en vivo:")
        for minutos, equipo1, resultado, equipo2 in partidosenvivo:
            mensaje += (f"\n{minutos:<5} {equipo1} {resultado} {equipo2}")
    elif uservivo == "NO JUGADOS":
        mensaje = ("Partidos sin jugar todavia:")
        for minutos, equipo1, resultado, equipo2 in partidosnoenvivo:
            mensaje += (f"\n{minutos:<5} {equipo1} {resultado} {equipo2}")
    elif uservivo == "FINALIZADOS":
        mensaje = ("Partidos finalizados: ")
        for minutos, equipo1, resultado, equipo2 in partidosfinalizados:
            mensaje += (f"\n{minutos:<5} {equipo1} {resultado} {equipo2}")
        
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
        time.sleep(15 * 60)  # Pausa de 15 minutos

    except Exception as e:
        print(f"Error al publicar el tweet: {e}")

# el timeset, es de prueba nomas, la idea es que el timeet este dentro de una funcion

horario.every(20).seconds.do(tweet) 

# el while para que se mantenga activo

print("Sigue funcionando")

while True:
    horario.run_pending() # verifica que no haya algo pendiente
    time.sleep(1) #crtl + c y frena el programa
