import datetime
from time import sleep
import cine35_download


class ba_date(datetime.date):
    """
    class used locally to print the date in french in slides
    """

    def __str__(self):
        months = ['fake', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'decembre']
        weekday = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return weekday[self.weekday()] + ' ' + str(self.day) + ' ' + months[self.month]


def addTrailer(file):
    """
    add a line in the file for a trailer
    :@param f: file object in which we will write
    """
    title = ''
    ba_url = ''
    end_date = datetime.datetime.now()
    broadcast_dates = []

    trailer = cine35_download.BandeAnnonce(title, ba_url, end_date, broadcast_dates)

    # titre
    while title == '':
        title = input('titre de la bande-annonce ? ')
        title = title or ''
    trailer.title = title

    # ba_url
    ba_url = input('url youtube à charger: \n')
    ba_url = ba_url or ''
    trailer.ba_url = ba_url

    # broadcast_dates
    while True:
        sdate = input('date de diffusion à ajouter [jj/mm/yyyy]: \n')
        sdate = sdate or ''
        if sdate == '':
            break
        date_array = sdate.split("/")
        try:
            day, month, year = date_array[0], date_array[1], date_array[2] 
            date = ba_date(int(year), int(month), int(day))
        except:
            print("Date non valide, merci de recommencer")
            continue

        hour = input('horaire: \n')
        hour = hour or ''
        broadcast_date = str(date) + ' à ' + hour
        trailer.broadcast_dates.append(broadcast_date)
        trailer.end_date = sdate
    
    file.write(str(trailer) + "\n")
