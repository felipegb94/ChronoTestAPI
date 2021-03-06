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

class User(db.Model):
	__tablename__ = 'Users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), index=True, unique = True)
	passwordHash = db.Column(db.String(200), unique = True)

	def __init__(self, username, pw):
		self.username = username
		self.passwordHash = pwd_context.encrypt(pw)

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


'''
Table for Tests. Each test name is unique and is the primary_key.
Parent of build_configs table (One-Many relation)
'''
class Tests(db.Model):
	__tablename__ = 'tests'

	id = db.Column(db.Integer, primary_key = True)
	timestamp = db.Column(db.DateTime, default = db.func.now())
	name = db.Column(db.String(50), index = True, primary_key = True, unique = True)
	project_name = db.Column(db.String(50), index = True)

	# Children elements
	build_configs = db.relationship('Build_Configs', backref = 'tests')

	def __init__(self, name, project_name):
		self.name = name
		self.project_name = project_name

	def __repr__(self):
		test = {"name": self.name,
                "project_name": self.project_name,  
                "id": self.id,
                "date_created": str(self.timestamp)}

		return json.dumps(test, indent = 4)

'''
Table for all Build_Configs each test from the tests table is run on. A test can have 
one to n number of configs it is run on. Each config is a row in this table.
Parent of: t_test_runs (One-Many relation)
'''
class Build_Configs(db.Model):

	__tablename__ = 'build_configs'

	id = db.Column(db.Integer, primary_key = True)
	builder_id = db.Column(db.String(100), index = True, primary_key = True, unique = True)
	hostname = db.Column(db.String(50), index = True)
	builder = db.Column(db.String(50), index = True)
	test_name = db.Column(db.String(50), db.ForeignKey('tests.name'), index = True)

	#Child Elements
	test_runs = db.relationship('Test_Runs', backref = 'tests', order_by = "Test_Runs.timestamp")

	def __init__(self, hostname, test_name, builder, builder_id):
		self.hostname = hostname
		self.builder = builder
		self.test_name = test_name
		self.builder_id = builder_id

	def __repr__(self):
		build_config = {"hostname": self.hostname,
                	   "builder": self.builder,  
                	   "test_name": self.test_name,  
                	   "builder_id": self.builder_id,  
                       "id": self.id}

		return json.dumps(build_config, indent = 4)

'''
Table with all the test_runs for all build configs of a test. A test which
is run under a certain config will have many runs and each run is a row in this
table.
'''
class Test_Runs(db.Model):

	__tablename__ = "test_runs"

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(120), index = True, unique = True) # Unique name
	test_name_builder = db.Column(db.String(100), db.ForeignKey('build_configs.builder_id'), index = True) 
	timestamp = db.Column(db.DateTime, default = db.func.now()) # When did it run.
	commit_id = db.Column(db.String(40), index = True) # Git commit id
	metrics = db.Column(JSON, index = False) # Metrics recorded during test.
	passed = db.Column(db.Boolean) # Test passed? 
	execution_time = db.Column(db.Float, index = True) # How long did the test run?


	def __init__(self, test_name_builder, commit_id, metrics, execution_time, passed):

		# Get count to get create a unique name for the test
		count = Test_Runs.query.filter(Test_Runs.test_name_builder == test_name_builder).count()

		self.name = test_name_builder + str(count)
		self.test_name_builder = test_name_builder
		self.commit_id = commit_id		
		self.metrics = metrics
		self.execution_time = execution_time
		self.passed = passed


	def __repr__(self):
		t = {"name": self.name,
			 "test_name_builder": self.test_name_builder,
			 "timestamp": self.timestamp,
             "passed": self.passed,
             "commit_id": self.commit_id, 
             "metrics": self.metrics,                 
             "timestamp": str(self.timestamp),
             "id": self.id}

		return json.dumps(t, indent = 4)
