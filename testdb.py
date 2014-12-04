#!flask/bin/python

'''
This Script is to test the database and add dummy objects to it.
'''

from app import models, db
from flask import jsonify
import json

output = { "tests": []}

#{"names" : ["first","second"], "values" : [1,2] }

test = {
        "name": "first",
        "project_name": "Chrono", 
        "passed": False,
        "runtime": {"runtime_names": ["first","second"], 
                    "runtime_values": [1,2]},
        "timestamp": "",
        "id": 0,
        }  

t = models.Test(name = test["name"], 
				project_name = test["project_name"],
				passed = test["passed"], 
				runtime = test["runtime"])

db.session.add(t)
db.session.commit()

def getTestJson(t):
	test = {
                "name": "",
                "project_name": "Chrono", 
                "passed": False,
                "runtime": 0, 
                "timestamp": "",
                "id": 0,
                }
	test["name"] = t.name
	test["runtime"] = t.runtime
	test["project_name"] = t.project_name
	test["passed"] = t.passed
	test["id"] = t.id
	test["timestamp"] = t.timestamp
	return test

#output = { "tests": []}
#tests = models.Test.query.all()

#test = models.Test.query.filter(models.Test.name == "benchmark2").all()
#dictTest = json.loads(test[0])
#print tests

#print dictTest

db.session.close()