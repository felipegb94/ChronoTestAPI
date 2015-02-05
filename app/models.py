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

	name = db.Column(db.String(30), index = True, primary_key = True, unique = True)
	machine_name = db.Column(db.String(20), index = True)
	project_name = db.Column(db.String(20), index = True)
	runs = db.relationship('Test_Runs', backref = 'tests')


	def __init__(self, name, project_name, machine_name):
		self.name = name
		self.machine_name = machine_name
		self.project_name = project_name

	def __repr__(self):
		test = {"name": self.name,
                "machine_name": self.machine_name,  
                "project_name": self.project_name,  
                "id": self.id}

		return json.dumps(test, indent = 4)

class Test_Runs(db.Model):

	__tablename__ = "test_runs"

	id = db.Column(db.Integer, primary_key = True)
	test_name = db.Column(db.String(30), db.ForeignKey('tests.name'))
	passed = db.Column(db.Boolean)
	execution_time = db.Column(db.Float, index = True)
	timestamp = db.Column(db.DateTime, default = db.func.now())
	metrics = db.Column(JSON, index = False)
	commit_id = db.Column(db.String(30), index = True)

	def __init__(self, test_name, execution_time, metrics, passed, commit_id):
		self.test_name = test_name
		self.execution_time = execution_time		
		self.metrics = metrics
		self.passed = passed
		self.commit_id = commit_id


	def __repr__(self):
		t = {"test_name": self.test_name,
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

