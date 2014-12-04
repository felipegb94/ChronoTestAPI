from flask import render_template
import urllib2
import json
from app import app



@app.route('/')
@app.route('/index')
def index():
    title = 'Testing Infrastructure for Project Chrono'
    user = {'nickname': 'Felipe'}  # fake user
    tests = {
    			'test1': {'name':'test1' , 'runtime': 2},
    			'test2': {'name': 'test2', 'runtime': 3}
    		}
    return render_template('index.html',
                           title=title,
                           user=user,
                           tests = tests)

