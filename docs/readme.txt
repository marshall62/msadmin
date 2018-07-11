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

----------------------------

I added the requests library which required installing pipenv as follows:

pip install --user pipenv
cd /srv/raiddisk/dev/pydev/msadmin
pipenv install requests

cd /srv/raiddisk/dev/pydev
source dj2mysqlenv/bin/activate
(env) pip3 install requests
(env) deactivate

On rose:

cd /mnt/net/django/msadmin
source env-msadmin-py345-dj2/bin/activate
(env) sudo pip3 install requests
(env) deactivate

---------------------------------------------------------------------
NOtes on Upgrading to Django 2.0 on 2/26/18:

Mr Charlie:

cd /srv/fastdisk/dev/pythondev/msadmin
virtualenv -p python3 dj2-env
source dj2-env/bin/activate
() pip3 install mysqlclient
() pip3 install -U Django
() deactivate
Make Intellij project use this virtualenv:
Project Structure | Project | + | Python SDK | Add local | navigate to dj2-env/bin/python3.5
Name this python SDK something like dj2-env
Make sure project and modules all use this SDK
Verified that project is running with the correct django.   Run python in venv:

import django

print(django.VERSION) in some code and checking it prints 2.0.2

Place a similar line somewhere in server code and run webapp.  Make sure it is 2.0.2

Had to modify the ForeignKeys to have on_delete=models.PROTECT and some have related_model="+" where there is confusion about backward refs
Finally,  Django gives message that there 1 unapplied migration and so I followed its instructions and did
source dj2-env/bin/activate
() python3 manage.py migrate
I get this error:
?: (mysql.W002) MySQL Strict Mode is not set for database connection 'default'
	HINT: MySQL's Strict Mode fixes many data integrity problems in MySQL, such as data truncation upon insertion, by escalating warnings into errors. It is strongly recommended you activate it. See: https://docs.djangoproject.com/en/2.0/ref/databases/#mysql-sql-mode
But I find that the database is defined in settings.py and has the below which is supposed to take care of this problem.
'OPTIONS': {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"





On Rose (upgrade to Django 2)

cd /mnt/net/django/msadmin
virtualenv env-msadmin-py345-dj2
source /env-msadmin-py345-dj2/bin/activate
() pip3 install mysqlclient
() pip3 install -U Django
() deactivate

Edit /etc/httpd/conf.d/wsgi.conf to use this new venv

Update the database to be compatible with django 2

Make sure the MathspringServer db user has ALTER privileges on db!

source /env-msadmin-py345-dj2/bin/activate
() python3 manage.py migrate

restart httpd

---------------------------------------------

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
my password to login to Mr Charlie  (on rose it is my user /pw for rose)


Development stuff:

DJango Shell:  Can interact with models and other code.
I am not able to get the shell running correctly from Intellij Tools menu.

Must cd to project root in a term window:
activate the venv by doing : source myenv/bin/activate
(venv)python3 manage.py shell

from msadmin.models import Strategy
Strategy.objects.all()

from msadmin.models import *
from msadmin.dbops.classops import *
validateSCISMaps_have_necessary_is_param_sc ()

I cannot figure out how to reload a module into this shell to enable bug fixing.  SOmething like this should work:
    To reload or reimport a module after fixing a bug
    import importlib
    importlib.reload(msadmin.dbops.classops)

deactivate



For routine deployment to rose:

location: /mnt/net/django/msadmin

If changes have been made to the msadminsite/settings.py file make a safe copy of the version on rose because it has settings
in it that are different than the ones on a dev machine.  This file is omitted from the git repo (via .gitignore) so new versions need to moved onto
rose using scp

ssh marshall@rose.cs.umass.edu
cd /mnt/net/django/msadmin
git pull

hand-merge the safe copy of settings.py with the one being moved using scp.

Set
export STATIC_ROOT='/mnt/net/http/msadmin_static/'

Run the command to move static into above dir so apache serves
cd /mnt/net/django/msadmin
source env-msadmin-py3-4/bin/activate
(venv)python manage.py collectstatic -n
This will pretend to move the files.  Verify that it moves them to the correct place and then do:
(venv)python manage.py collectstatic

Alternative to the above is to move files by hand from /msadmin_static into /mnt/net/http/msadmin_static

Make sure database tables have been updated if necessary (see below)

restart apache.
sudo /etc/init.d/httpd restart

deactivate // will leave the virtualenv

URLS to test:
http://rose.cs.umass.edu/msadmin/classes/
http://rose.cs.umass.edu/msadmin/class/1022/
http://rose.cs.umass.edu/msadmin/admin/

superuser: marshall / mr charlie password


Updating the db:

All the tables involved in the tutoring strategy are new and can be moved (with data) into the rose db without worry of
ruining existing data.

Once the tutoring strategies go into use, this won't be true and I'll have to work differently.

Tables involved:
wayangoutpostdb_class_sc_is_map.sql
wayangoutpostdb_class_sc_param.sql
wayangoutpostdb_intervention_selector.sql
wayangoutpostdb_is_param_base.sql
wayangoutpostdb_is_param_class.sql
wayangoutpostdb_is_param_sc.sql
wayangoutpostdb_is_param_value.sql
wayangoutpostdb_lc.sql
wayangoutpostdb_sc_class.sql
wayangoutpostdb_sc_is_map.sql
wayangoutpostdb_sc_param_map.sql
wayangoutpostdb_sc_param.sql
wayangoutpostdb_strategy_class.sql
wayangoutpostdb_strategy_component.sql
wayangoutpostdb_strategy.sql

Export them in a single file folder within /srv/raiddisk/wodbs/stratXXX

OPen a rose db window
MAKE SURE YOU ARE IN ROSE DB:
load the file docs/dbload.sql which will remove all these tables from the rose DB
Now import what you exported.


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
marshall62@gmail.com my mr charlie password

Test:
python manage.py runserver
Can only hit the localhost:8000

Set up mod_wsgi for apache as in /etc/httpd/conf.d/wsgi.conf
(last line is specific for centos)
WSGISocketPrefix /var/run/wsgi

Note that the wsgi.conf has the path to the virtualenv that will run
WSGIDaemonProcess rose.cs.umass.edu python-home=/mnt/net/django/msadmin/env-msad
min-py3-4 python-path=/mnt/net/django/msadmin

2/24/18 Upgraded to Django 2 and created a new virtualenv
 /env-msadmin-py34-dj2

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







