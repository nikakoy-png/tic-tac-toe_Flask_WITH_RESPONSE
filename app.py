import time

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api
from flask_jwt_extended import JWTManager

from config import ConfigClass
from resources.routes import init_router
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')

db = MongoEngine(app)
api = Api(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)
init_router(api)

# CELERY
from celery import Celery

# celery config
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'


celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



if __name__ == '__main__':
    app.debug = True
    app.run()
