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

Open up `config_var_example.py` and change the `SQLALCHEMY_DATABASE_URI` to the URI of your postgresql database. In my case my database is `postgresql://localhost/chronoTest`. Also change the `SECRET_KEY` to what your secret key will be (this can be any randome phrase). Finally rename `config_var_example.py` to `config_var.py` 

Run the following 3 commands:
```
python migrate.py db init
python migrate.py db migrate
python migrate.py db upgrade
```

Authentication in this API is a password based authentication. Your database will have a Users table and it should have a 
