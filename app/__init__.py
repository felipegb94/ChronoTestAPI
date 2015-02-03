from flask import Flask
from flask.ext.restful  import Api
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_hmac import Hmac


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
hm = Hmac(app)


api = Api(app)


from app import views, models
from app import chronoTestApi

#if __name__ == '__main__':
   # manager.run()