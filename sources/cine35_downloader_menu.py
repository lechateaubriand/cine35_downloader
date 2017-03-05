#!/usr/bin/env python
from cursesmenu import *
from cursesmenu.items import *
from time import sleep
import ba_dl_variables
import cine35_download
import cine35_file_maker


def make_file():
    file = input('Chemin du fichier à créer [%s]: ' % ba_dl_variables.default_file)
    file = file or ba_dl_variables.default_file

    f = open(file, 'w')
    while True:
        choice = input('Ajouter une bande-annonce o/n [o] ? ')
        choice = choice or 'o'
        if choice == 'o' or choice == 'O':
            cine35_file_maker.addTrailer(f)
        else:
            break
    f.close()
    print("'''''''''''''''''''''''''")
    print("fin de la construction du fichier")
    print("'''''''''''''''''''''''''")
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
menu = CursesMenu("Cine35 Downloader", "Choisissez l'une des options suivantes:")

# menu items
file_factory_item = FunctionItem("Construire le fichier de download", make_file)
download_item = FunctionItem("Lancer le downloader",  launch_downloader)

# Once we're done creating them, we just add the items to the menu
menu.append_item(file_factory_item)
menu.append_item(download_item)

# Finally, we call show to show the menu and allow the user to interact
menu.show()
