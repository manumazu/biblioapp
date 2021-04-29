MYSQL_DATABASE_USER = 'bibliobus'
MYSQL_DATABASE_PASSWORD  = 'bibliobus'
MYSQL_DATABASE_DB = 'bibliobus'
MYSQL_DATABASE_HOST = 'db'
MAIL_SERVER = 'localhost'
MAIL_PORT = 8025
MAIL_DEFAULT_SENDER = 'contact@bibliob.us'
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = 1800
#used for isbn search, key must be defined here : https://console.cloud.google.com/apis/credentials
GOOGLE_BOOK_API_KEY = ''
#key used for recaptcha v3, must be defined here : https://www.google.com/recaptcha/admin/
RECAPTCHA_SECRET = ''
#must set a strong key chain to encode / decode jwt
SECRET_KEY = ''
#define email of account who is allowed to set up bibus modules 
SHELF_ADMIN_EMAIL = ''

