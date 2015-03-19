ChronoTestAPI
=============

API of the testing infrastructure for Chrono

Setup:

Clone the repository
```
git clone git@github.com:felipegb94/ChronoTestAPI.git
```

Start a virtualenv
```
virtualenv chronoapi
source chronoapi/bin/activate
```

Install the required packages
```
pip install -r requirements.txt
```

If you have not created a database yet continue to read this. If you have already created the database, skip this paragraph. In order to create a database make sure you have the postgresql server running. Once it is running just run the following command:
```
createdb NAME_OF_YOUR_DATABASE
```
In my case the name of the database in chronoTest.

Open up `config_var_example.py` and change the `SQLALCHEMY_DATABASE_URI` to the URI of your postgresql database. In my case my database is `postgresql://localhost/chronoTest`. Also change the `SECRET_KEY` to what your secret key will be (this can be any randome phrase). Finally rename `config_var_example.py` to `config_var.py` 

Run the following 3 commands:
```
python migrate.py db init
python migrate.py db migrate
python migrate.py db upgrade
```

Authentication in this API is a password based authentication. Your database will have a Users table where it will save username and a passwordHash. Therefore the first thing you have to do before people start using the API, is to add users to your database. In order to do this open the create_user.py script and edit the following line with the correct credentials:
```
newUser = models.User("newUsername", "samplePassword")
```
After adding all the users that will be using your API now they can start making requests to it.
