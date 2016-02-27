# -*- coding: utf-8 -*-
import os
import subprocess
import threading
import youtube_dl
import time
import datetime
from time import sleep, mktime, strptime
import ba_dl_variables
import ba_dl_thread
from dbus.exceptions import DBusException
import logging, logging.config
logging.config.dictConfig(ba_dl_variables.LOGGING)


def main(csv_file):
    """
    fonction qui prend en entree le csv file, le parse et lance les download
    ainsi que la preparation du slide_template
    """
    whole_ba = BandeAnnonceList(csv_file)

    for each in whole_ba.ba_list:
        t = BaDownloadThread(each.title, each.ba_url, each.end_date, each.broadcast_dates, slide_template=ba_dl_variables.slide_template)
        t.start()
        sleep(10)


class BandeAnnonce(object):
    """
    Classe representant une bande_annonce avec ses attributs:
    self.title (string)
    self.end_date (datetime.datetime)
    self.ba_url (string)
    self.broadcast_dates (list of strings)
    """
    def __init__(self, title, ba_url, end_date, broadcast_dates):
        self.title = title
        self.end_date = end_date
        self.ba_url = ba_url
        self.broadcast_dates = broadcast_dates


class BandeAnnonceList(object):
    """
    Classe initialise par un fichier csv avec une ligne par bande annonce
    chaque ligne comprend:
    colonne 1: titre
    colonne 2: lien youtube
    colonne 3: end_date au format dd/mm/yyyy
    colonne 4 a 6

    la classe BandeAnnonce ne contient qu'un attribut:
    self.bande_annonce_list = []
    """

    def __init__(self, csv_file):
        self.ba_list = []
        self.parse(csv_file)


    def parse(self, csv_file):

        with open(csv_file, 'r') as csv_file:
            content = csv_file.readlines()

        for each in content:
            line = map(lambda x: x.rstrip(), each.split(';'))
            line_end_date = line[2].split('/')
            current_end_date = datetime.date(int(line_end_date[2]), int(line_end_date[1]), int(line_end_date[0]))
            current_broadcast_dates = map(lambda x: x.decode('utf-8'), line[3:len(line)])
            current_ba = BandeAnnonce(line[0].decode('utf-8'), line[1], current_end_date, current_broadcast_dates)
            self.ba_list.append(current_ba)


class BaDownloadThread(threading.Thread):
    """
    Thread qui download une ba depuis youtube et cree le slide associe
    end_date is datetime.datetime
    broadcast_date is a list of string
    """

    def __init__(self, title, ba_url, end_date, broadcast_dates, slide_template=None):
        super(BaDownloadThread, self).__init__()
        self.ba_url = ba_url
        self.slide_template = slide_template
        self.title = title
        self.broadcast_dates = broadcast_dates
        self.end_date = end_date


    def run(self):
        logging.info("in download_ba_from_youtube: %s, %s" % (self.ba_url, self.end_date))
        logging.info(str(type(self.end_date)))

        prefix = str(self.end_date.year) + "_" + str(self.end_date.month) + "_" + str(self.end_date.day) + "__"

        # traitement de la video    
        ydl_opts = {
            'format': 'best[height=720]',
            'outtmpl': os.path.join(ba_dl_variables.ba_directory, prefix + "%(title)s.%(ext)s"),
            'restrictfilenames': True,
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                logging.debug("before extract_info")
                info_dict = ydl.extract_info(self.ba_url, download=True)
                logging.debug("after extract_info")
                # sanitize_filename est applique par YoutubeDL quand restrictfilenames=True
                # je le rappelle ici pour conserver le meme nom de fichier
                video_title = youtube_dl.utils.sanitize_filename(info_dict.get("title", None), restricted=True)
                video_ext = info_dict.get('ext', None)
                filename = prefix + video_title + '.' + video_ext
                logging.info("the file %s has been downloaded into %s" %(filename, ba_dl_variables.ba_directory))

        except Exception as e:
            logging.error("the file could not be dowloaded: " + str(e))
            raise

        # traitement du slide
        if self.slide_template is not None:
            command = ["convert -font /usr/share/fonts/truetype/freefont/FreeSansOblique.ttf -pointsize 65 -fill red -draw 'text 100,240 \"" + self.title + "\" ' "]
            i = 0
            for each in self.broadcast_dates:
                if i == 0:
                    command.append("-pointsize 45 -fill white -draw 'text 150,350 \"" + each + "\" ' ")
                elif i == 1:
                    command.append("-pointsize 45 -fill white -draw 'text 150,450 \"" + each + "\" ' ")
                elif i == 2:
                    command.append("-pointsize 45 -fill white -draw 'text 150,550 \"" + each + "\" ' ")
                i = i+1
            command.append(self.slide_template)
            command.append(os.path.join(ba_dl_variables.ba_directory, ''.join([prefix, video_title, '.jpg'])))
            decoded_command = map(lambda x: x.encode('utf-8'), command)
            final_command = ' '.join(decoded_command)
            logging.info("creating the slide for %s" % video_title)
            result = subprocess.call(final_command, shell=True)
            try:
                assert result==0
            except:
                logging.error("trouble in slide preparation for %s" % video_title)



class BaDownloadAndFtpUploadThread(threading.Thread):
    """
    Thread qui download une ba depuis youtube puis l'upload sur le serveur ftp
    """

    def __init__(self, ba_url, end_date):
        super(BaDownloadThread, self).__init__()
        self.ba_url = ba_url
        self.end_date = end_date
        #self.stoprequest = threading.Event()

    def run(self):
        logging.info("in download_ba_from_youtube_and_upload_to_ftpserver: %s, %s" % (self.ba_url, self.end_date))
        logging.info(str(type(self.end_date)))
    
        prefix = str(self.end_date.year) + "_" + str(self.end_date.month) + "_" + str(self.end_date.day) + "__"
        
        ydl_opts = {
            'format': 'best[height=720]',
            'outtmpl': os.path.join(ba_dl_variables.ba_directory, prefix + "%(title)s.%(ext)s"),
            'restrictfilenames': True,
        }
    
        try:
            # download from youtube
            filepath = ''
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.ba_url, download=True)
                # sanitize_filename est applique par YoutubeDL quand restrictfilenames=True
                # je le rappelle ici pour conserver le meme nom de fichier
                video_title = youtube_dl.utils.sanitize_filename(info_dict.get("title", None), restricted=True)
                video_ext = info_dict.get('ext', None)
                filename = prefix + video_title + '.' + video_ext
                logging.info("the file %s has been downloaded into %s" %(filename, ba_dl_variables.ba_directory))
                filepath = os.path.join(ba_dl_variables.ba_directory, filename)
        except:
            logging.error("the file could not be dowloaded")
            raise
    
        try:
            #upload to ftpserver
            os.chdir(ba_dl_variables.ba_directory)
            ftp = FTP(ba_dl_variables.ftp_server)
            ftp.login(ba_dl_variables.ftp_login, ba_dl_variables.ftp_passwd)
            ftp.cwd(ba_dl_variables.ftp_home_dir)
    
            with open(filepath, 'rb') as fhandle:
                logging.info('Ftp Copying ' + filename)
                ftp.storbinary('STOR ' + filename, fhandle) 
                logging.info('File %s has been uploaded to ftp server' % filename)
            ftp.quit()
        except:
            logging.error("the file could not be uploaded to ftpserver")
            raise
    
if __name__ == "__main__":

    main('/media/claire/4E53-05B4/sauvegarde/programme.csv')