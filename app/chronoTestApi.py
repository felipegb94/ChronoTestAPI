from flask import jsonify, make_response, abort, request, g
from flask.ext.restful import Resource, reqparse, fields, marshal
from app import app, api
from app import db, models, hm
from flask.ext.httpauth import HTTPBasicAuth
import json

auth = HTTPBasicAuth()

'''
Function used by HTTPBasicAuth to do password verification for every
Resource that has the login_required decorator.
'''
@auth.verify_password
def verify_password(username_or_token, password):
    user = models.User.verify_auth_token(username_or_token)

    if not user:
        user = models.User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False

    g.user = user

    return True

'''
Once a user has logged in, he is given a key to make future requests for a
period of time.
'''
@app.route('/chrono_test/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

'''
These are the keys every test should have.
'''
def Keys():
    keys = ["name", "project_name", "metrics", "execution_time", "passed"]

    return keys

'''
Validate that each test in the json file contains the required keys.
'''
def validateTest(data):

    keys = Keys()

    for key in keys:
        if(not key in data):
            message = "Missing " + key + " argument provided. Required to create a test"
            abort(400)

    return True

'''
Resource to query all tests in the Test table through get and to
add a new set of test_runs through post. 
'''
class TestListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.testParser = reqparse.RequestParser()

        #Required format for input
        self.reqparse.add_argument('tests', type = list, required = True,
            help = 'No test list provided. Required to create a test',             
            location = 'json')
        self.reqparse.add_argument('config', type = dict, required = True,
            help = 'No config of the machine being used provided.',
            location = 'json')

      
        super(TestListAPI, self).__init__()

    def get(self):

        tests = models.Test.query.all()

        return json.loads(str(tests))

    #Create New 
    def post(self):
        
        args = self.reqparse.parse_args()
        tests = args.get("tests")
        config = args.get("config")
        machine_name = config.get("build_info").get("hostname")
        latest_commit = config.get("repos_data").get("commitID")

        for t in tests:
            validateTest(t)
            new_test = models.Test.query.filter(models.Test.name == t.get("name")).first()

            if(new_test == None):
                new_test = models.Test(name = t.get("name"),
                                       machine_name = machine_name,
                                       project_name = t.get("project_name"))
                db.session.add(new_test)
                db.session.commit()

            new_test_run = models.Test_Runs(test_name = t.get("name"),
                                            passed = t.get("passed"),
                                            execution_time = t.get("execution_time"),
                                            metrics = t.get("metrics"),
                                            commit_id = latest_commit) 
            db.session.add(new_test_run)
            db.session.commit() 
            
        numTests = models.Test.query.all()

        return {"numTests" : len(numTests)}, 201


        
api.add_resource(TestListAPI, '/chrono_test/api/tests', endpoint = 'tests')

'''
Resource that allows you to get all test_runs from a specific test through get.
'''
class TestAPI(Resource):

    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, required = True,
            help = 'Every test has to have a name in order to find it.', location = 'json')
        self.reqparse.add_argument('passed', type = bool,
            location = 'json')
        self.reqparse.add_argument('project_name', type = str,
            location = 'json')
        self.reqparse.add_argument('runtime', type = int, 
            help = 'The only field that can be updated is runtime.', location = 'json')
        super(TestAPI, self).__init__()

    def get(self, test_name):

        t = models.Test.query.filter(models.Test.name == test_name).first()

        #Abort if there is no test with that name.
        if(t == None):
            abort(404)

        return json.loads(str(t.runs))
        
api.add_resource(TestAPI, '/chrono_test/api/tests/<string:test_name>', endpoint = 'test')

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error 401': 'Unauthorized access. Your username or password are incorrect.'}), 401)