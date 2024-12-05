import tweepy as tw
import schedule as horario
from dotenv import load_dotenv
import time
import random
import os


# las credenciales para que se asocie la account, utilizo el .env porque por lo que lei es mas seguro a la hora de subir a repositorios
# y eso, cosa de no regalarse viste.

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
bearer_token = os.getenv("BEARER_TOKEN")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# cuerpo

client = tw.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

mensaje_aleatorio = ("A", "E", "I", "O", "U")

# la funcion del twitteo 

def tweet():

    # para que no se repita el tweet (only testeo)

    texto = random.choice(mensaje_aleatorio)

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

horario.every(35).minutes.do(tweet) 

# el while para que se mantenga activo

print("Sigue funcionando")

while True:
    horario.run_pending() # verifica que no haya algo pendiente
    time.sleep(1) #crtl + c y frena el programa

