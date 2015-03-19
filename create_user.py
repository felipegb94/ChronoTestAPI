from app import models, db
'''
Edit this file to create users of the API. Only users who send the right 
credential (username, password) in their http request will be able to
use the API
'''
newUser = models.User("newUsername", "samplePassword")
db.session.add(newUser)
db.session.commit()
