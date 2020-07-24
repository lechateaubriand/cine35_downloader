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
        weekday = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        return weekday[self.weekday()] + ' ' + str(self.day) + ' ' + months[self.month]


def addTrailerFromApi(file, movie_info):
    """
    add a line in the file for a trailer
    :@param f: file object in which we will write
    :@param trailer_infos: a list of dict. Each dict is one of the backoffice entry for this movie.
    """
    title = movie_info[0]['film_titre']
    ba_url = movie_info[0]['ba_youtube']
    end_date = datetime.date(1984, 1, 1)
    broadcast_dates = []


    for info in movie_info:
        # convert date
        date_array = info['date'].split("/")
        day, month, year = int(date_array[0]), int(date_array[1]), int(date_array[2])
        converted_date = ba_date(year, month, day)

        # convert hour
        current_broadcast_date = datetime.date(year, month, day)
        if (current_broadcast_date > end_date):
            end_date = current_broadcast_date

        # get hour and VOSTF if exists
        hour_array = info['heure'].split(":")
        hour = "h".join(hour_array)
        seance_type = ''
        if 'VOSTF' in info['types_seance']:
            seance_type = ' (VOSTF)'

        # final broadcast date string
        broadcast_date = str(converted_date) + ' à ' + hour + seance_type
        broadcast_dates.append(broadcast_date)

    end_date = '%s/%s/%s' % (end_date.day, end_date.month, end_date.year)
    trailer = cine35_download.BandeAnnonce(title, ba_url, end_date, broadcast_dates)

    file.write(str(trailer) + "\n")


def addTrailerFromMenu(file):
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
        title = input('\ntitre de la bande-annonce ? \nutiliser \\n pour materialiser le retour à la ligne\n \
exemple: Ma vie de courgette\\nCinépitchoune\n ')
        title = title or ''
    trailer.title = title

    # ba_url
    ba_url = input('\nurl youtube à charger: \n')
    ba_url = ba_url or ''
    trailer.ba_url = ba_url

    # broadcast_dates
    while True:
        sdate = input('\ndate de diffusion à ajouter [jj/mm/yyyy]: \n')
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

        hour = input('\nhoraire: \n')
        hour = hour or ''
        broadcast_date = str(date) + ' à ' + hour
        trailer.broadcast_dates.append(broadcast_date)
        trailer.end_date = sdate
    
    file.write(str(trailer) + "\n")
