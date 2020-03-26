from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserType(Enum):
        Hospital = 'Hospital'
        Supplier = 'Supplier'
        HospitalGroup = 'HospitalGroup'

    user_type = models.CharField(
        max_length=100,
        choices=[(tag.value, tag.name) for tag in UserType],
        blank=False,
        null=False,
    )


class HospitalGroup(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)


class Hospital(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)
    reputation_score = models.FloatField(blank=True, null=True)
    hospital_group = models.ForeignKey(HospitalGroup, on_delete=models.CASCADE, blank=False, null=False)
    only_within_group = models.BooleanField(blank=False, null=False, default=False)


class Supplier(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)


class Order(models.Model):
    num_requested = models.IntegerField(null=False, blank=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)
    time_submitted = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    auto_generated = models.BooleanField(blank=False, null=False, default=False)


class Ventilator(models.Model):
    class State(Enum):
        Available = 'Available'
        Requested = 'Requested'
        InTransit = 'InTransit'
        InUse = 'InUse'

    model_num = models.CharField(max_length=128)
    state = models.CharField(
        max_length=100,
        choices=[(tag.value, tag.name) for tag in State],
        blank=False,
        null=False,
        default=State.Available,
    )
    owning_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=False, null=False, related_name='owning_hospital')
    current_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=False, null=False, related_name='current_hospital')
    batch_id = models.CharField(max_length=128, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)

class ShipmetBatches(models.Model):
    max_batch_id = models.IntegerField(blank=False, null=False)
