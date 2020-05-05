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
from enum import Enum

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser

from django.db.models.signals import pre_init, pre_save

class User(AbstractUser):
    inserted_at = models.DateTimeField(auto_now_add=True)
    inserted_by_user  = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_inserted_by_user',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by_user  = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_updated_by_user',
    )
    is_valid = models.BooleanField(default=True)

    def set_current_type(self, entityType):
        self.current_type = entityType

    def get_roles(self):
        roles = {
            'hospital': [],
            'hospital_group': [],
            'supplier': [],
            'system': []
        };
        for role in self.user_role_user.all():
            if role.hospital_group:
                roles['hospital_group'].append(role.hospital_group)
            elif role.hospital:
                roles['hospital'].append(role.hospital)
            elif role.supplier:
                roles['supplier'].append(role.supplier)
            else:
                roles['system'].append(role.system)
        return roles

    def get_current_role(self):
        return UserRole.get_default_role(self)

class AbstractCommon(models.Model):
    inserted_at = models.DateTimeField(auto_now_add=True)
    inserted_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
        related_name='%(class)s_inserted_by_user',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
        related_name='%(class)s_updated_by_user',
    )
    is_valid = models.BooleanField(default=True)
    class Meta:
        abstract = True

# How to insert the first user SYSTEM with id=0?
# SYSTEM user is used to set user fields when system-generated or
# system-updated.

class System(AbstractCommon):
    name = models.CharField(max_length=100, default='System')
    users = models.ManyToManyField(
        User,
        through='UserRole',
        through_fields=('system','assigned_user'),
    )
    
class HospitalGroup(AbstractCommon):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(
        User,
        through='UserRole',
        through_fields=('hospital_group','assigned_user'),
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
        through_fields=('hospital','assigned_user'),
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
        through_fields=('supplier','assigned_user'),
    )
    
class UserRole(AbstractCommon):
    class Role(Enum):
        Admin = 'Admin'
        Manager = 'Manager'
        Operator = 'Operator'
        Shipper = 'Shipper'
        NoRole = 'NoRole'

    assigned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_role_user')
    granted_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_role_granted_by_user')
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
    # This is a Private Field! Do not access it directly! 
    # until we impose some restriction, exactly 1 role per user should be set to true.
        # Upon user creation, this is the last role created.
        # If a new role is made (by a new association), that is automatically made the last used role (make sure the last one is made false)
    _last_used_role = models.BooleanField(default=True)

    def get_entity(self):
        if self.hospital:
            return self.hospital
        elif self.hospital_group:
            return self.hospital_group
        elif self.supplier:
            return self.supplier
        else:
            return self.system
    @staticmethod
    def clear_roles(user):
        role = UserRole.get_default_role(user)
        if role == None:
            return
        role._last_used_role = False
        role.save()

    @staticmethod
    @transaction.atomic
    def make_default_role(user, new_role):
        UserRole.clear_roles(user)
        new_role._last_used_role = True
        new_role.save()

    @staticmethod
    def get_default_role(user):
        return UserRole.objects.filter(assigned_user=user).filter(_last_used_role=True).first()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['assigned_user', 'system'],
                                    name='user_system_uq'),
            models.UniqueConstraint(fields=['assigned_user', 'hospital'],
                                    name='user_hospital_uq'),
            models.UniqueConstraint(fields=['assigned_user', 'hospital_group'],
                                    name='user_hospital_group_uq'),
            models.UniqueConstraint(fields=['assigned_user', 'supplier'],
                                    name='user_supplier_uq'),
        ]
def update_last_used_role(sender, **kwargs):
    kwarg = kwargs['kwargs']
    if (len(kwarg) == 0):
        return
    UserRole.clear_roles(kwarg['assigned_user'])

pre_init.connect(update_last_used_role, sender=UserRole)

class Request(AbstractCommon):
    class Status(Enum):
        PendingApproval = 'PendingApproval'
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
        default=Status.PendingApproval.name,
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    requested_qty = models.IntegerField()
    allocated_qty = models.IntegerField(default=0)
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
        related_name='request_opened_by_user',
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    approved_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='request_approved_by_user',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='request_cancelled_by_user',
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='request_closed_by_user',
    )
    closed_at = models.DateTimeField(null=True, blank=True)

class Offer(AbstractCommon):
    class Status(Enum):
        PendingApproval = 'PendingApproval'
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
#       PendingApproval -> Closed (lack of actions)
#       PendingApproval -> Cancelled -> Closed
#       PendingApproval -> Replaced -> Closed
#       PendingApproval -> Approved -> Closed (most common flow)
#       PendingApproval -> Approved -> Replaced -> Closed
#       PendingApproval -> Approved -> Cancelled -> Closed

    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.PendingApproval.name,
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
    offered_qty = models.IntegerField()
    allocated_qty = models.IntegerField(default=0)
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
        related_name='offer_opened_by_user',
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    approved_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='offer_approved_by_user',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    replaced_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='offer_replaced_by_user',
    )
    replaced_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='offer_cancelled_by_user',
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='offer_closed_by_user',
    )
    closed_at = models.DateTimeField(null=True, blank=True)

class Allocation(AbstractCommon):
    class Status(Enum):
        Allocated = 'Allocated'
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
        default=Status.Allocated.name,
    )
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    allocated_qty = models.IntegerField()
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=0,
        related_name='allocation_opened_by_user',
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    approved_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='allocation_approved_by_user',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='allocation_cancelled_by_user',
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='allocation_closed_by_user',
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
        RequestedReserve = 'RequestedReserve'
#       Receiving hospital has requested that the destination reserve ventilators be released
        Cancelled = 'Cancelled'
#       any unshipped allocation is also cancelled
        Closed = 'Closed'
#       has been reviewed and closed by requesting hospital
#       
        # If a shipment is open, it can become packed or cancelled
        # If it's packed it can become shipped or cancelled. If it's shipped we need the tracking number and the service used.
        # It it's shipped, it can only arrive.
        # If it has arrived, for now it can only go to Accepted.
        # From Arrived, it can go to Requested Reserve
            # From Requested Reserve, it can go back to Accepted if the request is denied, it can go to Closed if reserve called back or if reserve deployed.

#       Open -> Closed (lack of actions)
#       Open -> Cancelled -> Closed
#       Open -> Packed -> Cancelled -> Closed
#       Open -> Packed -> Shipped -> Arrived -> Accepted -> Closed
#       Two ways to go from Accepted to Closed. Either Destination Reserve is deployed or it's called back.
    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.Open.name,
    )
    allocation = models.ForeignKey(Allocation, on_delete=models.CASCADE)
    # this can be referenced with [shipment_ventilator.ventilator for shipment_ventilator in shipment.shipment_ventilator_set.all()], since order of declaration matters in Django.
    # Essentially we have a circular reference that cannot be resolved unless one is removed.
    # ventilators = models.ManyToManyField(
    #     Ventilator,
    #     through='ShipmentVentilator',
    # )
    shipped_qty = models.IntegerField(default=0)
    opened_by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    opened_at = models.DateTimeField(auto_now_add=True)
    packed_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shipment_packed_by_user',
    )
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shipment_shipped_by_user',
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    arrived_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shipment_arrived_by_user',
    )
    arrived_at = models.DateTimeField(null=True, blank=True)
    accepted_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shipment_accepted_by_user',
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shipment_cancelled_by_user',
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    closed_by_user  = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shipment_closed_by_user',
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    shipping_service = models.CharField(max_length=100, null=True, blank=True)
    is_requisition = models.BooleanField(null=False, blank=False, default=False)
# Had to move this down to ensure that Shipment was declared before Ventilator since Ventilator references it. I can also remove 
# the reference and replace it with a query if efficiency isn't a huge deal here?

class VentilatorModel(AbstractCommon):
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    monetary_value = models.IntegerField(default=10000)
    image = models.CharField(max_length=200, null=True, blank=True)

class Ventilator(AbstractCommon):
    class Status(Enum):
        Unavailable = 'Unavailable'
        Available = 'Available'
        Arrived = 'Arrived'
        Packing = 'Packing'
        InTransit = 'In Transit'
        SourceReserve = 'Source Reserve'
        DestinationReserve = 'Destination Reserve'

    class UnavailableCode(Enum):
        Unknown = 'Unknown'
        InUse = 'In Use'
        PendingOffer = 'Pending Offer'
        TestingNeeded = 'Testing Needed'
        InTesting = 'In Testing'
        NotWorking = 'Not Working'
        InRepair = 'In Repair'

    class ArrivedCode(Enum):
        NeedsInspection = 'NeedsInspection'
        PassInspection = 'PassInspection'
        DestinationReserve = 'DestinationReserve'
        AvailableForUse = 'AvailableForUse'

    class Quality(Enum):
        Poor = 'Poor'
        Fair = 'Fair'
        Excellent = 'Excellent'

    status = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in Status],
        default=Status.Unavailable.name
    )
    unavailable_code = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in UnavailableCode],
        default=UnavailableCode.InUse.name,
        null=True,
        blank=True
    )
    arrived_code = models.CharField(
        max_length=100,
        choices=[(tag.name, tag.value) for tag in ArrivedCode],
        default=ArrivedCode.AvailableForUse.name,
        null=True,
        blank=True
    )
    serial_number = models.CharField(max_length=100, null=False, blank=False)
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
        related_name='ventilator_owning_hospital',
    )
    current_hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ventilator_current_hospital',
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
        related_name='shipment_last_shipment',
    )
    monetary_value = models.IntegerField()
#   default to ventilator_model.monetary_value
    image = models.CharField(max_length=200, null=True, blank=True)
    quality = models.CharField(
        max_length=100,
        null=True, 
        blank=True, 
        choices=[(tag.name, tag.value) for tag in Quality],
        default=Quality.Poor.name
    )

class ShipmentVentilator(AbstractCommon):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    ventilator = models.ForeignKey(Ventilator, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shipment', 'ventilator'],
                                    name='shipment_ventilator_uq'),
        ]

class SystemParameters(AbstractCommon):
    destination_reserve = models.FloatField(blank=False, null=False, default=0.0)
    strategic_reserve = models.FloatField(blank=False, null=False, default=0.0)
    reputation_score_weight = models.FloatField(blank=False, null=False, default=34.0)
    contribution_weight = models.FloatField(blank=False, null=False, default=33.0)
    projected_load_weight = models.FloatField(blank=False, null=False, default=33.0)

    @staticmethod
    @transaction.atomic
    def getInstance():
        params = SystemParameters.objects.first()
        if not params:
            params = SystemParameters()
            params.save()
        return params
