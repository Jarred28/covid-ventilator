from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserType(Enum):
        Hospital = 'Hospital'
        Supplier = 'Supplier'

    user_type = models.CharField(
        max_length=100,
        choices=[(tag.value, tag.name) for tag in UserType],
        blank=False,
        null=False,
    )


class Hospital(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)


class Supplier(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)


class Ventilator(models.Model):
    model_num = models.CharField(max_length=128)
