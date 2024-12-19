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

    partidos(uservivo, partidosenvivo, partidosnojugados, partidosfinalizados, driver)

# Ejecutar la función principal
main()