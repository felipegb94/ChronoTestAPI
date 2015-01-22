from app import db
import json
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON, ARRAY

class Test(db.Model):

	__tablename__ = "tests"
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, default=db.func.now())
	name = db.Column(db.String(20), index=True)
	project_name = db.Column(db.String(20), index=True)
	execution_time = db.Column(db.Float, index = True)
	metrics = db.Column(JSON, index=False)
	passed = db.Column(db.Boolean, index=True)

	def __init__(self, name, project_name, execution_time, metrics, passed):
		self.name = name
		self.project_name = project_name
		self.execution_time = execution_time		
		self.metrics = metrics
		self.passed = passed


	def __repr__(self):
		test = {"name": self.name,
                "project_name": self.project_name,  
                "passed": self.passed,
                "execution_time": self.execution_time, 
                "metrics": self.metrics,                 
                "timestamp": str(self.timestamp),
                "id": self.id}

		return json.dumps(test, indent = 4)

class User(db.Model):
	__tablename__ = "Users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), index=True, unique = True)
	passwordHash = db.Column(db.String(200), unique = True)

	def __init__(self, username, password):
		self.username = username
		self.passwordHash = password

	def set_password(self, password):
		self.passwordHash = generate_password_hash(password)

	def check_password(self, password):
		check_password_hash(self.passwordHash, password)

	def __repr__(self):
		return '<User %r>' % (self.username)

