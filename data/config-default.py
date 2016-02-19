import os

# TELEGRAMBOT
WEBHOOK_URL = ''
LANGUAGE = 'en_EN'
TOKEN = ''
LOCALE_DIR = 'locale'
DB_NAME = 'telegrambot' # Name of your mongo database
TIMEZONE = 'Europe/Madrid' #Other examples: 'US/Eastern' 'Asia/Tokyo'

# FLASK
DEBUG = False
PROPAGATE_EXCEPTIONS = True
SECRET_KEY = os.environ.get('SECRET_KEY','\xfb\x13\xdf\xa1@i\xd6>V\xc0\xbf\x8fp\x16#Z\x0b\x81\xeb\x16')
HOST_NAME = os.environ.get('OPENSHIFT_APP_DNS','localhost')
APP_NAME = os.environ.get('OPENSHIFT_APP_NAME','flask')
IP = os.environ.get('OPENSHIFT_PYTHON_IP','127.0.0.1')
PORT = int(os.environ.get('OPENSHIFT_PYTHON_PORT',8080))

# MONGODB
MONGO_USER = os.environ.get('OPENSHIFT_PYTHON_IP','admin')
MONGO_IP = os.environ.get('OPENSHIFT_MONGODB_DB_HOST','127.0.0.1')
MONGO_PORT = os.environ.get('OPENSHIFT_MONGODB_DB_PORT',27017)
MONGO_PASSWORD = os.environ.get('OPENSHIFT_MONGODB_DB_PASSWORD')
MONGO_URL = os.environ.get('OPENSHIFT_MONGODB_DB_URL')  # MongoDB connection URL (e.g. mongodb://<username>:<password>@<hostname>:<port>/)
MONGO_PORT = os.environ.get('OPENSHIFT_MONGODB_DB_LOG_DIR')
