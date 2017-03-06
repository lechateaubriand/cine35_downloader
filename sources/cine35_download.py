# -*- coding: utf-8 -*-
import os
import subprocess
import threading
import youtube_dl
import time
import datetime
from time import sleep, mktime, strptime
import ba_dl_variables
from dbus.exceptions import DBusException
import logging, logging.config
logging.config.dictConfig(ba_dl_variables.LOGGING)


def main(csv_file, ba_directory):
    """
    fonction qui prend en entree le csv file, le parse et lance les download
    ainsi que la preparation du slide_template
    """
    whole_ba = BandeAnnonceList(csv_file)

    for each in whole_ba.ba_list:
        t = BaDownloadThread(each.title, each.ba_url, each.end_date, each.broadcast_dates, ba_directory, slide_template=ba_dl_variables.slide_template)
        t.start()
        t.join()


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

    def __str__(self):
        to_join = [self.title, self.ba_url, str(self.end_date)]
        to_join.extend(self.broadcast_dates)
        return ";".join(to_join)


class BandeAnnonceList(object):
    """
    Classe initialise par un fichier csv avec une ligne par bande annonce
    chaque ligne comprend:
    colonne 1: titre
    colonne 2: lien youtube
    colonne 3: end_date au format dd/mm/yyyy
    colonne 4 a x: string contenant une date de diffusion

    la classe BandeAnnonceList ne contient qu'un attribut:
    self.bande_annonce_list = []
    """

    def __init__(self, csv_file):
        self.ba_list = []
        self.parse(csv_file)


    def parse(self, csv_file):

        utf8_csv_file = self._convert_to_utf8(csv_file)

        with open(utf8_csv_file, 'r') as csv_file:
            content = csv_file.readlines()

        for each in content:
            line = list(map(lambda x: x.rstrip(), each.split(';')))
            line_end_date = line[2].split('/')
            current_end_date = datetime.date(int(line_end_date[2]), int(line_end_date[1]), int(line_end_date[0]))
            
            # on enleve les dates vides dues a la sauvegarde excel vers csv
            unfiltered_broadcast_dates = map(lambda x: x, line[3:len(line)])
            current_broadcast_dates = []
            for each in unfiltered_broadcast_dates:
                if each != '':
                    current_broadcast_dates.append(each)
            
            # creation de la bande annonce complete
            current_ba = BandeAnnonce(line[0], line[1], current_end_date, current_broadcast_dates)
            self.ba_list.append(current_ba)

    def _convert_to_utf8(self, csv_file):

        tmp_file = "/tmp/" + os.path.basename(csv_file) + ".utf8.csv"

        # find the file charset format using file command
        command = "file -i " + csv_file
        #charset_full = subprocess.run(command, check=True, stdout=subprocess.PIPE, encoding="utf-8").stdout
        charset_full = subprocess.check_output(command, shell=True, universal_newlines=True)
        charset = charset_full.split("=")[1].rstrip()

        # convert to utf-8
        if charset.lower() != "utf-8":
            command = "iconv -f " + charset + " -t utf-8 " + csv_file + " -o " + tmp_file
            print(command)
            try:
                subprocess.check_call(command, shell=True)
                return tmp_file
            except:
                logging.error("problème au moment de la conversion du fichier en utf-8")
                logging.error("convertir le fichier en utf8 avant de re-essayer")
                raise
        return csv_file


class BaDownloadThread(threading.Thread):
    """
    Thread qui download une ba depuis youtube et cree le slide associe
    end_date is datetime.datetime
    broadcast_date is a list of string
    """

    def __init__(self, title, ba_url, end_date, broadcast_dates, ba_directory, slide_template=None):
        super(BaDownloadThread, self).__init__()
        self.ba_url = ba_url
        self.slide_template = slide_template
        self.title = title
        self.broadcast_dates = broadcast_dates
        self.end_date = end_date
        self.ba_directory = ba_directory


    def _date_text_for_slide_creation(self):
        i = 0
        command=[]
        if len(self.broadcast_dates) < 4:
            for each in self.broadcast_dates:
                if i == 0:
                    command.append("-pointsize 45 -fill white -draw 'text 150,350 \"" + each + "\" ' ")
                elif i == 1:
                    command.append("-pointsize 45 -fill white -draw 'text 150,450 \"" + each + "\" ' ")
                elif i == 2:
                    command.append("-pointsize 45 -fill white -draw 'text 150,550 \"" + each + "\" ' ")
                i = i+1
        elif len(self.broadcast_dates) == 4:
            for each in self.broadcast_dates:
                if i == 0:
                    command.append("-pointsize 42 -fill white -draw 'text 150,300 \"" + each + "\" ' ")
                elif i == 1:
                    command.append("-pointsize 42 -fill white -draw 'text 150,380 \"" + each + "\" ' ")
                elif i == 2:
                    command.append("-pointsize 42 -fill white -draw 'text 150,460 \"" + each + "\" ' ")
                elif i == 3:
                    command.append("-pointsize 42 -fill white -draw 'text 150,540 \"" + each + "\" ' ")
                i = i+1
        elif len(self.broadcast_dates) == 5:
            for each in self.broadcast_dates:
                if i == 0:
                    command.append("-pointsize 35 -fill white -draw 'text 150,290 \"" + each + "\" ' ")
                elif i == 1:
                    command.append("-pointsize 35 -fill white -draw 'text 150,360 \"" + each + "\" ' ")
                elif i == 2:
                    command.append("-pointsize 35 -fill white -draw 'text 150,430 \"" + each + "\" ' ")
                elif i == 3:
                    command.append("-pointsize 35 -fill white -draw 'text 150,500 \"" + each + "\" ' ")
                elif i == 4:
                    command.append("-pointsize 35 -fill white -draw 'text 150,570 \"" + each + "\" ' ")
                i = i+1
        return command


    def _title_text_for_slide_creation(self):
        # si presence d'une apostrophe, il faut ajouter \\ devant l'apostrophe
        # sinon plantage de la fonction convert
        self.title = self.title.replace("'", "\\\\'")

        if len(self.title) <= 25:
            command = ["convert -font /usr/share/fonts/truetype/freefont/FreeSansOblique.ttf -pointsize 65 -fill red -draw \"text 100,240 '" + self.title + "' \" "]
        else:
            command = ["convert -font /usr/share/fonts/truetype/freefont/FreeSansOblique.ttf -pointsize 55 -fill red -draw \"text 100,240 '" + self.title + "' \" "]
        return command


    def run(self):
        logging.info("in download_ba_from_youtube: %s, %s, %s" % (self.title, self.ba_url, self.end_date))
        logging.info(str(type(self.end_date)))

        prefix = str(self.end_date.year) + "_" + str(self.end_date.month) + "_" + str(self.end_date.day) + "__"

        # traitement de la video    
        ydl_opts = {
            #'format': 'best[height=720]',
            'format': 'best',
            'outtmpl': os.path.join(self.ba_directory, prefix + "%(title)s.%(ext)s"),
            'restrictfilenames': True,
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.ba_url, download=True)
                # sanitize_filename est applique par YoutubeDL quand restrictfilenames=True
                # je le rappelle ici pour conserver le meme nom de fichier
                video_title = youtube_dl.utils.sanitize_filename(info_dict.get("title", None), restricted=True)
                video_ext = info_dict.get('ext', None)
                filename = prefix + video_title + '.' + video_ext
                logging.info("the file %s has been downloaded into %s" %(filename, self.ba_directory))

        except Exception as e:
            logging.error("the file could not be dowloaded: " + str(e))
            raise

        # traitement du slide
        if self.slide_template is not None:
            command = self._title_text_for_slide_creation()
            command.extend(self._date_text_for_slide_creation())
            command.append(self.slide_template)
            command.append(os.path.join(self.ba_directory, ''.join([prefix, video_title, '.jpg'])))
            #decoded_command = map(lambda x: x.encode('utf-8'), command)
            decoded_command = list(map(lambda x: x, command))
            final_command = ' '.join(decoded_command)
            logging.info("command pour la creation du slide: %s" % final_command)
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
            'outtmpl': os.path.join(self.ba_directory, prefix + "%(title)s.%(ext)s"),
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
                logging.info("the file %s has been downloaded into %s" %(filename, self.ba_directory))
                filepath = os.path.join(self.ba_directory, filename)
        except:
            logging.error("the file could not be dowloaded")
            raise
    
        try:
            #upload to ftpserver
            os.chdir(self.ba_directory)
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

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file', help="full path of the csv file")
    parser.add_argument('-dir', '--directory', dest='ba_directory', help="full path of the directory where to save ba and slides")
    args = parser.parse_args()

    try:
        l_ba_directory = args.ba_directory
    except:
        l_ba_directory = ba_dl_variables.ba_directory

    main(args.csv_file, l_ba_directory)
