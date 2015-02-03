import os
import config_vars

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = config_vars.SQLALCHEMY_DATABASE_URI
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True #for security
SECRET_KEY = config_vars.SECRET_KEY
 

HMAC_KEY = config_vars.HMAC_KEY

