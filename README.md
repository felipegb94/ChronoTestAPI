ChronoTestAPI
=============

API of the testing infrastructure for Chrono

Setup:

1. Download the repository
2. Get the virtual environment started. At the top level of the repository in the command line type: "virtualenv flask"
3. Install the required packages
    pip install -r requirements.txt
4. Open up config.py and change the SQLALCHEMY_DATABASE_URI to the URI of your postgresql database. In my case my database is 'postgresql://localhost/chronoTest'
5. run the following 3 commands:</br>
-flask/bin/python migrate.py db init</br>
-flask/bin/python migrate.py db migrate</br>
-flask/bin/python migrate.py db upgrade</br>

