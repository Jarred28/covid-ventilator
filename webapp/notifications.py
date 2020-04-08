import os
from django.core.mail import send_mail
from covid.settings import DEFAULT_EMAIL
# Assumes we get Hospital object for sender and recipient and int for amount

def send_ventilator_notification(sender, recipient, amount):
	subject = "Covid-19 Ventilator Notification - Request"
	body = "Hello {0}, {1} would like {2} ventilators. Please enter the platform to accept or decline.".format(sender.name, recipient.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [sender.user.email])

def send_transit_notification(recipient, amount):
	subject = "Covid-19 Ventilator Notification - Transit"
	body = "Hello {0}, {1} ventilators are in transit to your location. Please let us know when they have been received.".format(recipient.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])

def send_received_notification(sender, recipient, amount):
	subject = "Covid-19 Ventilators Notification - Received"
	body = "Hello {0}, {1} has received your {2} ventilators.".format(sender.name, recipient.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])

def send_requisitioned_email(sender, recipient, amount):
	subject = "Covid-19 Ventilators Notification - Requisitioned"
	body = "Hello {0}, unfortunately {1} has had a recent surge in cases and needs the {2} ventilators it had on reserve at your location. Please ship it back to them as soon as possible.".format(recipient.name, sender.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])

def send_deployable_email(sender, recipient, amount):
	subject = "Covid-19 Ventilators Notification - Deployable"
	body = "Hello {0}, {1} has determined that it will not see a spike in cases in the near future and is allowing you to deploy the {2} ventilators you had on reserve.".format(recipient.name, sender.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])

def send_denied_reserve_email(sender, recipient, amount):
	subject = "Covid-19 Ventilators Notification - Denied"
	body = "Hello {0}, {1} has denied your request to allow you to deploy their {2} ventilators on reserve.".format(recipient.name, sender.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])

def send_requested_reserve_email(sender, recipient, amount):
	subject = "Covid-19 Ventilators Notification - Requested"
	body = "Hello {0}, {1} has requested the {2} ventilators on reserve at your location. Please accept or deny in the Orders dashboard.".format(sender.name, recipient.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])
