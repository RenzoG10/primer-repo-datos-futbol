from funciones import *

# Función principal para buscar partidos

def main():
    # Solicitar fecha y país
    dia, mes, anio, fecha, paisbuscadoarreglado, uservivo = inputs()

    # Iniciar Selenium y BeautifulSoup
    driver, url, html, soup, grupos = selenium(fecha)

    ligas_y_partidos = buscar_partido(grupos)

    partidosenvivo, partidosnojugados, partidosfinalizados = filtrado_partidos_vivo_nojugados_finalizados(ligas_y_partidos, paisbuscadoarreglado)

    partidos(dia, mes, anio, uservivo, partidosenvivo, partidosnojugados, partidosfinalizados, driver)

# Ejecutar la función principal
if __name__ == "__main__":
    main()
