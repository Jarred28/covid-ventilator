# app
This is an app.

## Directory Structure
/env - virtualenv directory  
/covid/settings.py - contains setting info like directory structure, etc.  
/templates - html templates  
/webapp/admin.py - code to produce admin site
/webapp/forms.py - contains form code for the admin site
/webapp/models.py - database schema  
/webapp/permissions.py - user type permissions  
/webapp/serializers.py - contains serializers to build forms  
/webapp/validation.py - code to validate forms  
/webapp/views.py - contains control for UI  
/webapp/urls.py - attach urls to views  


## Installation / Run instructions (on localhost)
1. clone the repo
2. enter the repo
3. run `source env/bin/activate` (use `deactivate` to exit the virtualenv)
4. run `pip3 install -r requirements.txt`
5. set environment variables: SECRET_KEY, MAILGUN_SMTP_SERVER, MAILGUN_SMTP_PORT, MAILGUN_SMTP_LOGIN, MAILGUN_SMTP_PASSWORD (these can be requested from the other collaborators)
6. run the app on localhost `python3 manage.py runserver` (ctrl-c to exit)


## Migrations
Use the command `python3 manage.py makemigrations` and `python3 manage.py migrate` if you update the database.

## Requirements
Run `pip3 freeze > requirements.txt` to add any packages you installed via pip. This should be done after installing the requirements.


## Deployment
For future deploys on release branch:

1. Pull your changes over to the release branch.
2. Generate migrations locally and push up to release.
3. Deploy release branch on Heroku.

## Website Access

This website currently supports 4 types of users: Hospital (Admin), Hospital Group (CEO), Supplier, System Operator.

### Requesting Credentials (User Instructions)

On the login / home page ('/'), follow the link entitled `request credentials.` Enter your desired username and email address as well as the user type you need an account for. Then fill out the information in the section associated with that user type and click `submit.`

Please note that in order to create a Hospital (admin) user, a hospital group (ceo) must be created first.

### Requesting Credentials (Admin Instructions)

After submitting the form, an email will be sent to the admins at the `DEFAULT_EMAIL` address in /covid/settings.py with the relevant information for creating your account.

Navigate to the admin site ('/admin') to add the user. You will need a superuser account to login. This can be done by following the steps after running `python3 manage.py createsuperuser.` Then login to the admin site.

Once you have logged in to the admin site, click on the `+ Add` next to the User section of the dashboard. Using the information from the email, enter in the username, email, and user type. then fill out the section corresponding to the user type. The password can be set optionally. It is recommended that the password is not filled out. In this case, and email will be sent to the new user to have them reset their password. From this point, the user can access the site.

## User Features

### Hospital (Admin)

A hospital (admin) can perform order monitoring / creation and ventilator monitoring / adding.

A hospital (admin) can use the navigation bar to the `Ventilators` page to view information about the ventilators they currently have as well as add new ventilators to the system, either individually or as a batch (using csv upload).

A hospital (admin) can also request ventilators using the `Orders` page on the navigation bar. Here they can request ventilators and see information about their previous orders.

### System Operator

A system operator can execute the distribution algorithm and can update algorithm parameters.

To run the algorithm, they can navigate to the `Dashboard` page on their navigation bar and press the `Execute` button.

To adjust the algorithm parameters, they can navigate to the `Settings` page via the navigation bar. Here they can adjust the system-wide reserve percentages and the weights of different data fields.

### Hospital Group (CEO)

A Hospital Group (CEO) can approve the filling of orders by hospitals in its group / chain on the `Dashboard` page.

### Supplier

The supplier functionality has not been developed yet.
