from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    # the group of hospital (e.g. VA)
    hospital_group = models.CharField(max_length=100, blank=False, null=False)

class Supplier(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
