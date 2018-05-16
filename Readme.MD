**MSAdmin** is the Django/Python Authoring environment for adminstering Mathspring and creating math content for it.

The project is best developed in the __Intellij IDEA__ IDE and upon cloning should be very easy to set up.

**Preliminaries:**

- Make sure you have a Python 3 SDK on your machine including pip.
sudo apt-get install python3-pip

- Install virtualenv 

    `sudo pip3 install virtualenv` 

1. Clone the repo by doing something like:

    `git clone https://github.com/marshall62/msadmin.git`

   The msadmin directory it creates will the sources for MS Admin.

2. install the python libmysql-client

    `sudo apt-get install libmysqlclient-dev` 

3. (optional) install django

    `pip3 install -U Django`

4.  In the directory that contains msadmin dir create a virtualenv
```
> virtualenv -p python3 dj2mysqlenv
> source myenv/bin/activate
(dj2mysqlenv) pip3 install mysqlclient
(dj2mysqlenv) pip3 install -U Django
(dj2mysqlenv) deactivate
```

5. Intellij: 

- File | Settings | Plug-ins .  Browse Jetbrains plug-ins and install Python and whatever it depends on.
- Restart Idea

- File | Project Structure | SDKs | + 
- Install a Python SDK System Interpreter from the location where Python lives (usr/bin/python3.5)

-Install the Python virtualenv created in step 4.

File | Project Structure | SDKs | +

- Select Virtualenv environment /  Existing environment 
- Navigate to dir/dj2mysqlenv/bin/python3.5
- Now set the Project SDK to point to this virtualenv
- File | Project Structure | Project | Project SDK 

6.   Note that file msadminsite/settings.py is missing because it contains usernames and passwords that configure the system.
Request a copy from me @marshall62.

7.  Run | Edit Configurations.  Select Run Django-2 login page.  It may pop up a dialog.   Make sure it 
is using the correct python environment.   It should then load the browser with the main page of the MSAdmin site.

You may need to do some django db work to create a superuser so that you can login to the MSAdmin tool and administer
the database using django.






