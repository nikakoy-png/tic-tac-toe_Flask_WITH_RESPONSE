import os

if os.path.exists('env.py'):
    import env


class ConfigClass(object):
    """ Flask application config """
    # Flask settings
    MONGODB_SETTINGS = {
        'db': 'TIC_TAC_TOES',
        'host': "localhost:27017",
        # 'host': "mongodb+srv://nikakoy:Vv190920031209@cluster0.oait7ww.mongodb.net",
    }
    SECRET_KEY = "rewrwerwetqpoqwjepiotupioweqptuoqwe"
