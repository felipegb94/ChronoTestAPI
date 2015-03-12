from flask import render_template
import urllib2
import json
from app import app



@app.route('/')
@app.route('/index')
def index():
    title = 'Testing Infrastructure API for Project Chrono'

    return render_template('index.html',
                           title=title)

