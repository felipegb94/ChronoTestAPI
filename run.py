#!flask/bin/python
from app import app
app.run(port=app.config['PORT'],debug=True)