import os
from django.core.mail import send_mail
from covid.settings import DEFAULT_EMAIL
# Assumes we get Hospital object for sender and recipient and int for amount

def send_ventilator_notification(sender, recipient, amount):
	subject = "Covid-19 Ventilator Notification - Request"
	body = "Hello {0}, {1} would like {2:d} ventilators. Please enter the platform to accept or decline.".format(sender.name, recipient.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [sender.user.email])

def send_transit_notification(recipient, amount):
	subject = "Covid-19 Ventilator Notification - Transit"
	body = "Hello {0}, {1:d} ventilators are in transit to your location. Please let us know when they have been received.".format(recipient.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])

def send_received_notification(sender, recipient, amount):
	subject = "Covid-19 Ventilators Notification - Received"
	body = "Hello {0}, {1} has received your {2:d} ventilators.".format(sender.name, recipient.name, amount)
	send_mail(subject, body, DEFAULT_EMAIL, [recipient.user.email])