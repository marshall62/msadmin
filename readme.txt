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


Development stuff:

DJango Shell:  Can interact with models and other code.
I am not able to get the shell running correctly from Intellij Tools menu.

Must cd to project root in a term window:
activate the venv
python manage.py shell

from msadmin.models import Strategy
Strategy.objects.all()




For routine deployment to rose:

location: /mnt/net/django/msadmin
git pull

Set
export STATIC_ROOT='/mnt/net/http/msadmin_static/'

Run the command to move static into above dir so apache serves
cd /mnt/net/django/msadmin
source env-msadmin-py3-4/bin/activate
(venv)python manage.py collectstatic -n
This will pretend to move the files.  Verify that it moves them to the correct place and then do:
(venv)python manage.py collectstatic

Alternative to the above is to move files by hand from /msadmin_static into /mnt/net/http/msadmin_static

Make sure database tables have been updated if necessary

restart apache.

deactivate // will leave the virtualenv

URLS to test:
http://rose.cs.umass.edu/msadmin/classes/
http://rose.cs.umass.edu/msadmin/class/1022/
http://rose.cs.umass.edu/msadmin/admin/

superuser: marshall / t0mand3rs



Setting up rose to serve:

I have omitted the file msadminsite/settings.py from git to protect db passwords.
Currently I have it using the marshall user rather than WayangServer because it needs to create tables to support django
Eventually I should be able to switch back if I'm not doing python manage.py migrate

Pull the project from github
Create a virtualenv  and activate
pip3 install mysqlclient

python manage.py migrate creates some tables which needs my marshall account in settings.py
python manage.py createsuperuser

marshall
marshall62@gmail.com
t0mand3rs

Test:
python manage.py runserver
Can only hit the localhost:8000

Set up mod_wsgi for apache as in /httpd/conf.d/wsgi.conf
(last line is specific for centos)
WSGISocketPrefix /var/run/wsgi


The static directory should be served by apache because it is CSS.

Adjustments to settings.py
DEBUG = False
STATIC_URL = 'http://rose.cs.umass.edu/msadmin_static/'

Set
STATIC_ROOT = '/mnt/net/http/msadmin_static/'
run the command to move static into above dir so apache serves
(venv)python manage.py collectstatic -n
This will pretend to move the files.  Verify that it moves them to the correct place and then do:
(venv)python manage.py collectstatic

restart apache.







