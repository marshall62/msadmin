Setting up the project with necessary libs for talking to mysql and a virtualenv

We are using the library mysqlclient:
https://pypi.python.org/pypi/mysqlclient

Django's recommended library.
Friendly fork of the original MySQLdb, hopes to merge back some day
The fastest implementation, as it is C based.
The most compatible with MySQLdb, as it is a fork
Debian and Ubuntu use it to provide both python-mysqldb andpython3-mysqldb packages


1.   sudo apt-get install libmysqlclient-dev
2.   cd to project dir (pythondev)
3.   virtualenv -p python3 env
4.   source env/bin/activate
5.   (env) pip3 install mysqlclient
6.   (env) pip3 install django
7    (env) deactivate

TO use this python environment:

source env/bin/activate
(env)python3
>>> import MySQLdb

To use this env from Intellij:

Go to Project Settings and set the Project SDK to point to
mysite/myenv/bin/python3.5

Add a new Django Server Runtime environment using Edit Configuration

Open the project structure and make sure that the project root is correct and that the module has a Django facet that
correctly points to the settings.py and manage.py

The /srv/fastdisk/dev/msadmin/db/DbTest.py shows how to connect to the database.

To run the django admin stuff:
http://127.0.0.1:8000/admin/

python manage.py createsuperuser

marshall
marshall62@gmail.com
t0mand3rs

