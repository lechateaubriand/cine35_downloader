import sys

################
#  DIRECTORIES
################
ba_directory = '/var/cine35/trailer'


###############
# SLIDES
###############
slide_template = '/var/cine35/cine35_downloader/slide_template/template_slide.jpg'
slide_has_header = True
title_color = "red"


###############
# DEFAULT VALUE FOR MENU
###############
default_file = '/tmp/cine35_download.csv'
default_ba_dir = '/var/cine35/trailer'


################
#   FTP SERVER
################
ftp = False
ftp_server = '192.168.1.12'
#ftp_server = '127.0.0.1'
ftp_port = '21'
ftp_login = ''
ftp_passwd = ''
ftp_home_dir = ''
ftp_filematch = '*.mp4'


################
#  LOGS
################
log_file = '/var/log/cine35_downloader/cine35_downloader.log'
LOGGING = {
    'version': 1,
    'formatters': {
        'default_formatter': {
            'format': '%(asctime)s : %(levelname)s : %(message)s',
            'datefmt': '%d-%b-%Y %H:%M:%S'
            },
        },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
            'stream': sys.stdout,
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default_formatter',
            'filename': log_file,
            'maxBytes': 50000,
            'backupCount': 3,
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO'
    }
}