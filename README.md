know-thy-shelf
==============

Library book sorting and inventory.

sudo apt-get install python-pip python-dev build-essential

sudo pip install --upgrade pip

sudo pip install --upgrade virtualenv

sudo apt-get install git

sudo apt-get install mysql-server

sudo apt-get install python-mysqldb

mysql -u root -p

create database bookshelfdb;

git clone https://github.com/szweibel/know-thy-shelf.git

pip install -r requirements.txt

Change 'settings.cfg.template' to 'settings.cfg'

In settings.cfg, change the secret key to whatever you'd like, and fill in the appropriate info for Mysql.

python setup_database.py

sudo gunicorn -w 4 -b 0.0.0.0:5000 shelf:app

Now Know Thy Shelf is running on port 5000. Change the default password in settings.cfg
