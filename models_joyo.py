# CONVENTIONS
# 
# Database time zone should be UTC.
#
# All tables shall have the following three columns (necessary for data
# preservation, ETL, analytics, debugging, etc.):
#   inserted_at = models.DateTimeField(null=False, blank=False,
#                                      auto_now_add=True)
#   updated_at = models.DateTimeField(null=False, blank=False, auto_now=True)
#   is_valid = models.BooleanField(blank=False, null=False, default=True)
#
# The system shall never delete any rows; it shall instead set is_valid to
# FALSE.  All WHERE clauses should include "AND is_valid" to exclude
# "deleted" rows.
#
# Suffixes and prefixes:
# is_xxx for BOOLEAN
# xxx_at for DATETIME
# xxx_on for DATE
# xxx_qty for INTEGER quantity
#
# I used the suffix _at for timestamp, and _on for date; something I have used
# for decades to avoid mistakes in queries.  Good conventions.

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser

class AbstractCommon(models.Model):
    inserted_at = models.DateTimeField(auto_now_add=True)
    inserted_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
    )
    is_valid = models.BooleanField(default=True)
    class Meta:
        abstract = True

class User(AbstractUser):
    inserted_at = models.DateTimeField(auto_now_add=True)
    inserted_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_valid = models.BooleanField(default=True)

# How to insert the first user SYSTEM with id=0?
# SYSTEM user is used to set user fields when system-generated or
# system-updated.

class System(AbstractCommon):
    name = models.CharField(max_length=100, default='System')
    users = models.ManyToManyField(
        User,
        through='UserRole',
        through_fields=('system','user'),
    )
    
class HospitalGroup(AbstractCommon):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(
        User,
        through='UserRole',
        through_fields=('hospital_group','user'),
    )
    
class Hospital(AbstractCommon):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    # need to expand into street_1, street_2, city, state, postal_code
    reputation_score = models.FloatField(null=True, blank=True)
    hospital_group = models.ForeignKey(HospitalGroup, on_delete=models.CASCADE)
    users = models.ManyToManyField(
        User,
        through='UserRole',
        through_fields=('hospital','user'),
    )
    within_group_only = models.BooleanField(default=False)
    contribution = models.IntegerField(default=0)
    projected_load = models.IntegerField(default=0)
    current_load = models.IntegerField(default=0)
    
class Supplier(AbstractCommon):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(
        User,
        through='UserRole',
        through_fields=('supplier','user'),
    )
    
class UserRole(AbstractCommon):
    class Role(Enum):
        Admin = 'Admin'
        Manager = 'Manager'
        Operator = 'Operator'
        Shipper = 'Shipper'
        None = 'None'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    granted_by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Role]
    )
    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    hospital_group = models.ForeignKey(
        HospitalGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'system'],
                                    name='user_system_uq'),
            models.UniqueConstraint(fields=['user', 'hospital'],
                                    name='user_hospital_uq'),
            models.UniqueConstraint(fields=['user', 'hospital_group'],
                                    name='user_hospital_group_uq'),
            models.UniqueConstraint(fields=['user', 'supplier'],
                                    name='user_supplier_uq'),
        ]

class VentilatorModel(AbstractCommon):
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    monetary_value = models.IntegerField(default=10000)
    image = models.CharField(max_length=200, null=True, blank=True)

class Ventilator(AbstractCommon):
    class Status(Enum):
        Unknown = 'Unknown'
        Available = 'Available'
        InUse = 'In Use'
        InTransit = 'In Transit'

    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.Unknown,
    )
    ventilator_model = models.ForeignKey(
        VentilatorModel,
        on_delete=models.CASCADE,
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
#   if this ventilator is loaded or inserted by a supplier,
#   set supplier to the supplier and leave both owning_hospital and
#   current_hospital null
    owning_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    current_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
#   initially owning_hospital and current_hospital are null if
#   this ventilator is supplied/inserted by a supplier and supplier is set;
#   if this ventilator is loaded or inserted by a hospital,
#   set current_hospital to the hospital that inserts this ventilator and
#   owning_hospital can be defaulted to the same hospital if not provided;
#   once last_shipment is accepted, change status to Accepted from InTransit,
#   set current_hospital to last_shipment.allocation.request.hospital;
#   if owning_hospital is still null, set it to the same hospital
    last_shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    monetary_value = models.IntegerField()
#   default to ventilator_model.monetary_value
    image = models.CharField(max_length=200, null=True, blank=True)
    quality = models.IntegerField(null=True, blank=True)

class Request(AbstractCommon):
    class Status(Enum):
        Open = 'Open'
#       has not been approved, so cannot be allocated yet
        Approved = 'Approved'
#       can now be allocated
        Cancelled = 'Cancelled'
#       any unallocated quantity is cancelled,
#       any unshipped allocation is also cancelled
        Closed = 'Closed'
#       has been reviewed and closed by requesting hospital
#
#       Open -> Closed (lack of actions)
#       Open -> Cancelled -> Closed
#       Open -> Approved -> Closed (most common flow)
#       Open -> Approved -> Cancelled -> Closed

    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.Open,
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    requested_qty = models.IntegerField()
    allocated_qty = models.IntegerField(default=0)
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    approved_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    closed_at = models.DateTimeField(null=True, blank=True)

class Offer(AbstractCommon):
    class Status(Enum):
        Open = 'Open'
#       has not been approved, so cannot be allocated to requests yet
        Approved = 'Approved'
#       can now be allocated to requests
        Replaced = 'Replaced'
#       any unallocated quantity is cancelled;
#       usually this is because a new offer has been opened to replace this
        Cancelled = 'Cancelled'
#       any unallocated quantity is cancelled,
#       any unshipped allocation is also cancelled
        Closed = 'Closed'
#       has been reviewed and closed by offering hospital or supplier
#
#       Open -> Closed (lack of actions)
#       Open -> Cancelled -> Closed
#       Open -> Replaced -> Closed
#       Open -> Approved -> Closed (most common flow)
#       Open -> Approved -> Replaced -> Closed
#       Open -> Approved -> Cancelled -> Closed

    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.Open,
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    requests = models.ManyToManyField(Request, through='Allocation')
    requested_qty = models.IntegerField()
    allocated_qty = models.IntegerField(default=0)
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    approved_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    replaced_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    replaced_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    closed_at = models.DateTimeField(null=True, blank=True)

class Allocation(AbstractCommon):
    class Status(Enum):
        Open = 'Open'
#       has not been approved, so cannot be shipped yet
        Approved = 'Approved'
#       can now be shipped
        Cancelled = 'Cancelled'
#       any unshipped allocation is also cancelled
        Closed = 'Closed'
#       has been reviewed and closed by offering hospital or supplier
#
#       Open -> Closed (lack of actions)
#       Open -> Cancelled -> Closed
#       Open -> Approved -> Closed (most common flow)
#       Open -> Approved -> Cancelled -> Closed

    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.Open,
    )
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    allocated_qty = models.IntegerField()
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    approved_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    closed_at = models.DateTimeField(null=True, blank=True)

class Shipment(AbstractCommon):
    class Status(Enum):
        Open = 'Open'
#       has not been packed
        Packed = 'Packed'
#       has been packed and can now be shipped
        Shipped = 'Shipped'
#       has been shipped and is in transit
        Arrived = 'Arrived'
#       has arrived at requesting hospital
        Accepted = 'Accepted'
#       has been reviewed and accepted at requesting hospital
        Cancelled = 'Cancelled'
#       any unshipped allocation is also cancelled
        Closed = 'Closed'
#       has been reviewed and closed by requesting hospital
#
#       Open -> Closed (lack of actions)
#       Open -> Cancelled -> Closed
#       Open -> Packed -> Cancelled -> Closed
#       Open -> Packed -> Shipped -> Arrived -> Accepted -> Closed

    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.Open,
    )
    allocation = models.ForeignKey(Allocation, on_delete=models.CASCADE)
    ventilators = models.ManyToManyField(
        Ventilator,
        through='ShipmentVentilator',
    )
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    opened_at = models.DateTimeField(auto_now_add=True)
    packed_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    arrived_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    arrived_at = models.DateTimeField(null=True, blank=True)
    accepted_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    closed_at = models.DateTimeField(null=True, blank=True)

class ShipmentVentilator(AbstractCommon):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    ventilator = models.ForeignKey(Ventilator, on_delete=models.CASCADE)
