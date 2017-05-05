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

activate the venv
python manage.py shell

from msadmin.models import Strategy
Strategy.objects.all()




For deployment to rose:

I have omitted the file msadminsite/settings.py from git to protect db passwords.
Currently I have it using the marshall user rather than WayangServer because it needs to create tables to support django
Eventually I should be able to switch back if I'm not doing python manage.py migrate

I had to install python 3 from sources and build manually.  I followed Part 1 instructions here:
http://ask.xmodulo.com/install-python3-centos.html

This installed it in /usr/local/bin rather than /usr/bin .   That would be something to fix.
It meant editing the /etc/sudoers file so that its line:
secure_path = /sbin:/bin:/usr/sbin:/usr/bin
has the path to where python3 goes

Once this is in.  install mysqlclient.  I had to download it from
 https://pypi.python.org/pypi/mysqlclient#downloads

 I downloaded the file as tar.gz to my ~/Downloads dir

 I then cd into the dir and do
 make
 make install

 Now I'm able to activate a virtual env
 and do pip3 install django
pip3 install mysqlclient

python manage.py migrate creates some tables which needs my marshall account
python manage.py createsuperuser

marshall
marshall62@gmail.com
t0mand3rs

python manage.py runserver

Next:  Set up a reverse proxy in apache.

Using a simple one like I did for testauth leads to the same problem I with that where all the URLs
are missing the /msadmin context that the apache reverse proxy adds.
https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-centos-7

mod_wsgi.so needs to be built for apache 2.2.15 with python 3.5  (do not yum install it)
I downloaded the sources to ~marshall/Downloads/modwsgi and followed the installation instructions for CentOS.

The static directory should be served by apache because it is CSS.  Eventually that stuff could be removed
from github and placed within apache but for now I'll let django serve it.




