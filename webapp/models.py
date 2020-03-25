from enum import Enum

from django.db import models
from django.contrib.auth.models import User


class Hospital(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)


class Supplier(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)


class Profile(models.Model):
    class UserType(Enum):
        Hospital = 'Hospital'
        Supplier = 'Supplier'

    # the django auth object
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=100,
        choices=[(tag.value, tag.name) for tag in UserType],
        blank=False,
        null=False,
    )
    # only one of the following should be nonnull as determined by user_type
    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, blank=True, null=True)
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, blank=True, null=True)


class Ventilator(models.Model):
	model_num = models.CharField(max_length=128)
