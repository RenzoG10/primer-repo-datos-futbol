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

        goles_comienzo(equipo1, equipo2, resultado, minutos, driver)

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