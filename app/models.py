from app import app, db
import json
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

'''
This file is the database model. Each class represents a table. And Each
db.relationship represent a relationship of a column to a table. The only
relationship as of now is a one to many relation from Test to Test_Runs. There
is a single test that is run many times.
'''

class Test(db.Model):

	__tablename__ = "tests"
	id = db.Column(db.Integer, primary_key = True)

	name = db.Column(db.String(30), index = True, primary_key = True)
	machine_name = db.Column(db.String(20), index = True)
	test_run_name = db.Column(db.String(30), index = True, primary_key = True, unique = True)
	project_name = db.Column(db.String(20), index = True)
	runs = db.relationship('Test_Runs', backref = 'tests')


	def __init__(self, name, test_run_name, project_name, machine_name):
		self.name = name
		self.test_run_name = test_run_name
		self.machine_name = machine_name
		self.project_name = project_name

	def __repr__(self):
		test = {"name": self.name,
                "machine_name": self.machine_name,  
                "test_run_name": self.test_run_name,                 
                "project_name": self.project_name,  
                "id": self.id}

		return json.dumps(test, indent = 4)

class Test_Runs(db.Model):

	__tablename__ = "test_runs"

	id = db.Column(db.Integer, primary_key = True)
	test_name = db.Column(db.String(30), index = True)
	test_run = db.Column(db.String(30), db.ForeignKey('tests.test_run_name'), index = True)
	machine_name = db.Column(db.String(30), index = True)
	passed = db.Column(db.Boolean)
	execution_time = db.Column(db.Float, index = True)
	timestamp = db.Column(db.DateTime, default = db.func.now())
	metrics = db.Column(JSON, index = False)
	commit_id = db.Column(db.String(30), index = True)

	def __init__(self, test_name, test_run, machine_name, execution_time, metrics, passed, commit_id):
		self.test_name = test_name
		self.test_run = test_run
		self.machine_name = machine_name
		self.execution_time = execution_time		
		self.metrics = metrics
		self.passed = passed
		self.commit_id = commit_id


	def __repr__(self):
		t = {"test_name": self.test_name,
				"test_run": self.test_run,
				"machine_name": self.machine_name,
                "passed": self.passed,
                "execution_time": self.execution_time, 
                "metrics": self.metrics,                 
                "timestamp": str(self.timestamp),
                "commit_id": self.commit_id,
                "id": self.id}

		return json.dumps(t, indent = 4)

class User(db.Model):
	__tablename__ = 'Users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), index=True, unique = True)
	passwordHash = db.Column(db.String(200), unique = True)

	def __init__(self, username):
		self.username = username

	def hash_password(self, pw):
		self.passwordHash = pwd_context.encrypt(pw)

	def verify_password(self, pw):
		return pwd_context.verify(pw, self.passwordHash)

	def generate_auth_token(self, expiration = 1000):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None
		user = User.query.get(data['id'])
		return user


	def __repr__(self):
		return '<User %r>' % (self.username)



class t_Tests(db.Model):
	__tablename__ = 't_tests'

	id = db.Column(db.Integer, primary_key = True)
	timestamp = db.Column(db.DateTime, default = db.func.now())
	name = db.Column(db.String(30), index = True, primary_key = True, unique = True)
	project_name = db.Column(db.String(20), index = True)

	#Children elements
	build_config = db.relationship('t_build_slaves', backref = 't_tests')

	def __init__(self, name, project_name):
		self.name = name
		self.project_name = project_name

	def __repr__(self):
		test = {"name": self.name,
                "project_name": self.project_name,  
                "id": self.id,
                "date_created": self.timestamp}

		return json.dumps(test, indent = 4)

'''
t_Build_Slaves is an association table from t_Tests to t_Test_Runs.
'''

class t_Build_Slaves(db.Model):

	__tablename__ = 't_build_slaves'

	id = db.Column(db.Integer, primary_key = True)
	slave = db.Column(db.String(30), index = True)
	builder = db.Column(db.String(30), index = True)
	test_name = db.Column(db.String(30), db.ForeignKey('t_tests.name'), index = True)
	builder_id = db.Column(db.String(30), index = True, primary_key = True, unique = True)

	#Child Elements
	test_runs = db.relationship('t_test_runs', backref = 'tests')

	def __init__(self, slave, test_name, builder):
		self.slave = slave
		self.builder = builder
		self.name_left = test_name
		self.builder_id = test_name + '_' + builder

	def __repr__(self):
		build_slave = {"slave": self.slave,
                	   "builder": self.builder,  
                	   "test_name": self.test_name,  
                	   "builder_id": self.builder_id,  
                       "id": self.id}

		return json.dumps(build_slave, indent = 4)


class t_Test_Runs(db.Model):

	__tablename__ = "t_test_runs"

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(30), index = True)
	test_builder = db.Column(db.String(30), db.ForeignKey('t_build_slaves.builder_id'), index = True)
	timestamp = db.Column(db.DateTime, default = db.func.now())
	commit_id = db.Column(db.String(40), index = True)
	metrics = db.Column(JSON, index = False)
	passed = db.Column(db.Boolean)
	execution_time = db.Column(db.Float, index = True)


	def __init__(self, name, testName_builderName, timestamp, commit_id, metrics, passed):
		self.name = name
		self.test_builder = testName_builderName
		self.timestamp = timestamp
		self.commit_id = commit_id		
		self.metrics = metrics
		self.passed = passed


	def __repr__(self):
		t = {"name": self.name,
			 "test_builder": self.test_builder,
			 "timestamp": self.timestamp,
             "passed": self.passed,
             "commit_id": self.commit_id, 
             "metrics": self.metrics,                 
             "timestamp": str(self.timestamp),
             "id": self.id}

		return json.dumps(t, indent = 4)
