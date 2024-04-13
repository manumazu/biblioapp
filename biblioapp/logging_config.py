from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
    'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default',
    },
    'custom_handler': {
      'class' : 'logging.FileHandler',
      'formatter': 'default',
      'filename' : 'logs/app.log',
      'level'    : 'INFO'
    }},    
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'custom_handler']
    }
})