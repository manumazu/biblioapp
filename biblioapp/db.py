from flaskext.mysql import MySQL
from biblioapp import app

db = MySQL()

def get_db() :
	# MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'manu'
	app.config['MYSQL_DATABASE_PASSWORD'] = 'mdp'
	app.config['MYSQL_DATABASE_DB'] = 'bibliobus'
	app.config['MYSQL_DATABASE_HOST'] = 'localhost'
	db.init_app(app)
	conn = db.connect()
	cursor = conn.cursor()	
	return cursor