# app
This is an app.

## Directory Structure
/env - virtualenv directory  
/covid/settings.py - contains setting info like directory structure, etc.  
/webapp/views - contains control for UI  
/webapp/models.py - database schema  
/webapp/urls.py - attach urls to views  

## Installation / Run instructions (on localhost)
1) clone the repo
2) enter the repo
3) run `source env/bin/activate` (use `deactivate` to exit the virtualenv)
4) run `pip3 install -r requirements.txt`
5) set environment variables: SECRET_KEY
7) run the app on localhost `python3 manage.py runserver` (ctrl-c to exit)


## Migrations
Use the command `python3 manage.py makemigrations` and `python3 manage.py migrate` if you update the database.

## Requirements
Run `pip3 freeze > requirements.txt` to add any packages you installed via pip. This should be done after installing the requirements.
