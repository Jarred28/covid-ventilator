from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class UserType(Enum):
        Hospital = 'Hospital'
        Supplier = 'Supplier'
        HospitalGroup = 'HospitalGroup'
        SystemOperator = 'SystemOperator'

    user_type = models.CharField(
        max_length=100,
        choices=[(tag.value, tag.name) for tag in UserType],
        blank=False,
        null=False,
    )


class SystemOperator(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)


class HospitalGroup(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.name


class Hospital(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)
    reputation_score = models.FloatField(blank=True, null=True)
    hospital_group = models.ForeignKey(HospitalGroup, on_delete=models.CASCADE, blank=False, null=False)
    within_group_only = models.BooleanField(blank=False, null=False, default=False)
    contribution = models.IntegerField(blank=False, null=False, default=0)
    projected_load = models.IntegerField(blank=False, null=False, default=0)


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

class ShipmentBatches(models.Model):
    max_batch_id = models.IntegerField(blank=False, null=False)

class SystemParameters(models.Model):
    destination_reserve = models.FloatField(blank=False, null=False, default=0.0)
    strategic_reserve = models.FloatField(blank=False, null=False, default=0.0)
    reputation_score_weight = models.FloatField(blank=False, null=False, default=34.0)
    contribution_weight = models.FloatField(blank=False, null=False, default=33.0)
    projected_load_weight = models.FloatField(blank=False, null=False, default=33.0)
