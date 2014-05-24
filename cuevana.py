# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import time
import os


def create_results_folder():
    cuevana_folder = os.path.abspath(os.path.dirname(__file__))
    results_folder = os.path.join(cuevana_folder, "results")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    return results_folder


def get_episodios_por_temporada():

    results_folder = create_results_folder()

    response = requests.get("http://www.cuevana2.tv/listar-series/?id=38")

    cuevana_serie_page_soup = BeautifulSoup(response.text)

    div_temporadas = cuevana_serie_page_soup.select("div.serie_id_ep")[0]

    temporadas = div_temporadas.select("ul.episodios")

    filename = "url_%s.txt" % time.strftime("%Y%m%d%H%M%S")

    archivo_url = open(os.path.join(results_folder, filename), "w")

    for temporada in temporadas:
        id_temporada = temporada['id']

        archivo_url.write("Temporada: %s \n" % id_temporada)

        capitulos = temporada.select("li > a")

        for capitulo in capitulos:

            url_visor_capitulo = capitulo['href']
            titulo = capitulo.select("span.tit")[0].text

            archivo_url.write(titulo.encode('utf8') + "\n")
            print titulo

            try:
                url_video, url_subtitulo = \
                    get_url_download(titulo, url_visor_capitulo)
            except requests.exceptions.ConnectionError as connection_error:
                print "cannot access to: ", url_visor_capitulo
                print connection_error.message
                raise connection_error

            archivo_url.write(url_video + "\n")
            archivo_url.write(url_subtitulo + "\n")


def get_url_download(titulo, url_visor):
    try:
        visor_response = requests.get(url_visor)
    except requests.exceptions.ConnectionError:
        time.sleep(0.1)
        try:
            visor_response = requests.get(url_visor)
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
            visor_response = requests.get(url_visor)

    visor_soup = BeautifulSoup(visor_response.text)
    visor_iframe = visor_soup.select('iframe')
    if len(visor_iframe) > 0:
        visor_src = visor_iframe[0]['src']

    url_video, url_subtitulo = visor_src.split("file=")[1].split("sub=")
    return url_video, url_subtitulo


if __name__ == "__main__":

    get_episodios_por_temporada()