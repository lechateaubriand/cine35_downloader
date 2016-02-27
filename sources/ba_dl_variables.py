import sys

################
#  DIRECTORIES
################
ba_directory = '/var/bande_annonces'


###############
# SLIDES
###############
slide_template = '/var/bande_annonces_slide/template_1.jpg'


################
#   FTP SERVER
################
ftp = False
ftp_server = '192.168.1.12'
#ftp_server = '127.0.0.1'
ftp_port = '21'
ftp_login = 'etoile'
ftp_passwd = 'etoile'
ftp_home_dir = '/home/etoile'
ftp_filematch = '*.mp4'


################
#  LOGS
################
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
            'filename': '/var/log/ba_dl.log',
            'maxBytes': 50000,
            'backupCount': 3,
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG'
    }
}