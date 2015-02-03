from flask import jsonify, make_response, abort, request, g
from flask.ext.restful import Resource, reqparse, fields, marshal
from app import app, api
from app import db, models, hm
from flask.ext.httpauth import HTTPBasicAuth
import json

auth = HTTPBasicAuth()

'''
test_fields = {
    'name': fields.String,
    'passed': fields.Boolean,
    'execution_time': fields.Float,
    'project_name': fields.String
}
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

@app.route('/chrono_test/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

def Keys():
    keys = ["name", "project_name", "metrics", "execution_time", "passed"]

    return keys

#Validate that the input json file contains the required keys.
def validateTest(data):

    keys = Keys()

    for key in keys:
        if(not key in data):
            message = "Missing " + key + " argument provided. Required to create a test"
            abort(400)

    return True

class TestListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.testParser = reqparse.RequestParser()

        #Required format for input
        self.reqparse.add_argument('tests', type = list, required = False,
            help = 'No test list provided. Required to create a test',             
            location = 'json')

      
        super(TestListAPI, self).__init__()

    def get(self):

        tests = models.Test.query.all()

        return json.loads(str(tests))

    #Create New 
    def post(self):
        
        args = self.reqparse.parse_args()
        tests = args.get("tests")

        for t in tests:
            
            validateTest(t)        
            newTest = models.Test(name = t.get("name"),
                                  project_name = t.get("project_name"),
                                  passed = t.get("passed"),
                                  execution_time = t.get("execution_time"),
                                  metrics = t.get("metrics"))
            db.session.add(newTest)
            db.session.commit() 
            
        numTests = models.Test.query.all()

        return {"numTests" : len(numTests)}, 201


        
api.add_resource(TestListAPI, '/chrono_test/api/tests', endpoint = 'tests')

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

        tests = models.Test.query.filter(models.Test.name == test_name).all()

        if len(tests) == 0:
            abort(404)

        return json.loads(str(tests))
        
    #Update Task: We don't want to be able to modify tests
    '''
    def put(self, test_name):

        test = filter(lambda t: t['test_name'] == test_name, output['tests'])

        if len(test) == 0:
            abort(404)

        test = test[0]
        args = self.reqparse.parse_args() #parse input arguments

        #update arguments in test. In here we want to add one more data point to the test. Either if it passed or failed.
        for k, v in args.iteritems(): 
            if v != None:
                test[k] = v
        return { 'test': marshal(test, test_fields) }
    '''    
'''
    def delete(self, test_name):
        pass
'''
api.add_resource(TestAPI, '/chrono_test/api/tests/<string:test_name>', endpoint = 'test')

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error 401': 'Unauthorized access. Your username or password are incorrect.'}), 401)