#!/usr/bin/env python
from consolemenu import *
from consolemenu.items import *
from time import sleep
import requests
import json

import cine35_download
import cine35_file_maker

import logging, logging.config
import ba_dl_variables
logging.config.dictConfig(ba_dl_variables.LOGGING)
from pprint import pprint


def make_file_from_api():
    file = input('Chemin du fichier à créer [%s]: ' % ba_dl_variables.default_file)
    file = file or ba_dl_variables.default_file

    # get info from backoffice
    date_debut = input('Date de début des séances (format YYYY-MM-DD): ')
    response = requests.get('https://www.etoilecinema.fr/api/seances?date_debut=%s' % date_debut)
    backoffice_movies = json.loads(response.text)
    logging.info("Movies info received from backoffice: ")
    logging.info(backoffice_movies)

    f = open(file, 'w')

    distinct_titles = set([ movie['film_titre'] for movie in backoffice_movies ])
    for title in distinct_titles:
        movie_backoffice_infos = [ movie for movie in backoffice_movies if movie['film_titre'] == title ]
        cine35_file_maker.addTrailerFromApi(f, movie_backoffice_infos)

    f.close()
    print("'''''''''''''''''''''''''''''''''")
    print("fin de la construction du fichier")
    print("'''''''''''''''''''''''''''''''''")


def make_file_from_menu():
    file = input('Chemin du fichier à créer [%s]: ' % ba_dl_variables.default_file)
    file = file or ba_dl_variables.default_file

    f = open(file, 'w')
    while True:
        choice = input('Ajouter une bande-annonce o/n [o] ? ')
        choice = choice or 'o'
        if choice == 'o' or choice == 'O':
            cine35_file_maker.addTrailerFromMenu(f)
        else:
            break
    f.close()
    print("'''''''''''''''''''''''''''''''''")
    print("fin de la construction du fichier")
    print("'''''''''''''''''''''''''''''''''")
    sleep(2)
    

def launch_downloader():
    file = input('Fichier à utiliser [%s]: ' % ba_dl_variables.default_file)
    file = file or ba_dl_variables.default_file
    ba_dir = input('Répertoire dans lequel importer les bandes-annonces et les slides [%s]: ' \
                       % ba_dl_variables.default_ba_dir)
    ba_dir = ba_dir or ba_dl_variables.default_ba_dir
    cine35_download.main(file, ba_dir)
    print("'''''''''''''''''''''''''")
    print("fin du download des bande-annonces et des slides, les logs sont visibles dans le fichier:\n %s" \
          % ba_dl_variables.log_file)
    print("'''''''''''''''''''''''''")
    sleep(5)


# Create the menu
menu = ConsoleMenu("Cine35 Downloader", "Choisissez l'une des options suivantes:")

# menu items
# file_factory_from_api = FunctionItem("Construire le fichier de download depuis le back office", make_file_from_api)
file_factory_item = FunctionItem("Construire le fichier de download avec le menu", make_file_from_menu)
download_item = FunctionItem("Lancer le downloader",  launch_downloader)

# Once we're done creating them, we just add the items to the menu
# menu.append_item(file_factory_from_api)
menu.append_item(file_factory_item)
menu.append_item(download_item)

# Finally, we call show to show the menu and allow the user to interact
menu.show()
