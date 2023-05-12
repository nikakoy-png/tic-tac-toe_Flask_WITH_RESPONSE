import os

if os.path.exists('env.py'):
    import env


class ConfigClass(object):
    """ Flask application config """
    # Flask settings
    MONGODB_SETTINGS = {
        'db': 'TIC_TAC_TOES',
        'host': "localhost:27017",
    }
    SECRET_KEY = ""
