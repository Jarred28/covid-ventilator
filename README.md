# app
This is an app.

## Directory Structure
/env - virtualenv directory  
/covid/settings.py - contains setting info like directory structure, etc.  
/webapp/views.py - contains control for UI  
/webapp/models.py - database schema  
/webapp/urls.py - attach urls to views  
/webapp/admin.py - code to produce admin site   
/webapp/permissions.py - user type permissions  
/webapp/validation.py - code to validate forms  
/templates - html templates  

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


## Deployment
For future deploys on release branch:

1. Pull your changes over to the release branch.
2. Generate migrations locally and push up to release.
3. Deploy release branch on Heroku.
