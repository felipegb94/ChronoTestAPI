from app import app, db
import json
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

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

