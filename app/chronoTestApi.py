from flask import jsonify, make_response, abort, request, g
from flask.ext.restful import Resource, reqparse
from app import app, api
from app import db, models
from sqlalchemy import and_, or_
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
Resource to query all tests in the Test table through get and to
add a new set of test_runs through post. 
'''
class TestListAPI(Resource):
    decorators = [auth.login_required]

    # Initializes args.
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.testParser = reqparse.RequestParser()

        # Required format for input
        self.reqparse.add_argument('tests', type = list, required = True,
            help = 'No test list provided. Required to create a test',             
            location = 'json')
        self.reqparse.add_argument('config', type = dict, required = True,
            help = 'No config of the machine being used provided.',
            location = 'json')

      
        super(TestListAPI, self).__init__()

    '''
    Get all tests in the t_tests table. This won't return any build or test_runs
    information
    '''
    def get(self):

        tests = models.t_Tests.query.all()

        return json.loads(str(tests))

    '''
    Create New test_run entry for every test. If this is the first time a test
    will be run, then a new test entry + a test_run entry will be added to the
    database.
    '''
    def post(self):
        
        args = self.reqparse.parse_args()
        # List of tests
        tests = args.get("tests")
        # Dict with configuration information
        config = args.get("config")

        # Build information
        hostname = config.get("build_info").get("hostname")
        builder = config.get("build_info").get("builder")

        # Repository data
        latest_commit = config.get("repos_data").get("commitID")
        counter = 0

        for t in tests:

            test_name = t.get("name") # Get test name
            test_name_builder = test_name + '_' + builder # Create test_builder unique ID

            # Query db for a test with the name tets_name
            test = models.t_Tests.query.filter(models.t_Tests.name == test_name).first()

            # If test does not exist in db. Add the test to the Test table
            if(test == None):
                test = models.t_Tests(name = test_name,
                                      project_name = t.get("project_name"))
                db.session.add(test)

            build_config = models.t_Build_Configs.query.filter(models.t_Build_Configs.builder_id == test_name_builder).first()
            # If the test with that specific build config does not exist in the table, add a new build config row
            if(build_config == None):
                build_config = models.t_Build_Configs(test_name = test_name,
                                                      hostname = hostname,
                                                      builder = builder,
                                                      builder_id = test_name_builder)
                db.session.add(build_config)
            # Add a new test_run row in the test_runs table
            new_test_run = models.t_Test_Runs(test_name_builder = test_name_builder,
                                              commit_id = latest_commit,
                                              passed = t.get("passed"),
                                              execution_time = t.get("execution_time"),
                                              metrics = t.get("metrics"))
            counter = counter+1
            db.session.add(new_test_run)


        
        db.session.commit() # Push all new entries to database


        return {"numTestRunsAdded" : counter}, 201


        
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

        t = models.t_Tests.query.filter(models.t_Tests.name == test_name).first()
        if(t == None):
            #Abort if there is no test with that name.
            abort(404)

        #runs = models.Test_Runs.query.filter(models.Test_Runs.test_name == test_name).order_by(models.Test_Runs.test_run_name).all()
        build_configs = t.build_configs

        # Format of the return json
        tests = {"name": test_name, "run_names": [], "status": [], "latest_commits": [], "current_execution_times": []}

        for i in range(0,len(build_configs)):

            tests["run_names"].append(build_configs[i].builder_id)

            t_runs = build_configs[i].test_runs
            latest_run = t_runs[len(t_runs)-1]
            status = latest_run.passed
            latest_commit = latest_run.commit_id
            current_execution_time = latest_run.execution_time

            tests["latest_commits"].append(latest_commit)
            tests["status"].append(status)
            tests["current_execution_times"].append(current_execution_time)

            tests[build_configs[i].builder_id] = json.loads(str(t_runs))


        return tests
        
api.add_resource(TestAPI, '/chrono_test/api/tests/<string:test_name>', endpoint = 'test')

'''
Returns an error when a login fails
'''
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error 401': 'Unauthorized access. Your username or password are incorrect.'}), 401)