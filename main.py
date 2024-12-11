from funciones import *

# Función principal para buscar partidos

def main():

    # Solicitar fecha y país
    dia,mes,anio, fecha, paisbuscadoarreglado, equipo_buscado, uservivo = inputs()

    # Iniciar Selenium y BeautifulSoup
    driver, url, html, soup, grupos = selenium(fecha)

    titulo_liga, minutos, equipo1, resultado, equipo2, partido_encontrado, ligas_y_partidos, partidos_de_liga = buscar_partido(grupos, equipo_buscado)

    # Mostrar resultados
    print(f"\nFecha: {dia}/{mes}/{anio}")
    if not partido_encontrado:
        print(f"No juega {equipo_buscado} en esta Fecha")

    partidosenvivo, partidosnojugados, partidosfinalizados = filtrado_partidos_vivo_nojugados_finalizados(ligas_y_partidos, paisbuscadoarreglado)
                        
    if uservivo == "VIVO":
        print("Partidos en vivo:")
        for minutos, equipo1, resultado, equipo2 in partidosenvivo:
            print(f"{minutos:<20} {equipo1:<30} {resultado:<20} {equipo2:<30}")
    
        estado_previos = {}

        print("\nMonitoreando cambios en los resultados. Presione Ctrl+C para detener.")

        try:
            while True:

                estado_actual = {}

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
main()