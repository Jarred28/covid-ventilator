import functools

from django.core.mail import send_mail
from rest_framework import serializers

from . import views
from .models import HospitalGroup, SystemParameters, Ventilator, VentilatorModel, User, Request, Offer, Allocation, Shipment
from .utilities import get_hospital_group_choices
from .validation import validate_signup
from covid.settings import DEFAULT_EMAIL

class VentilatorModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VentilatorModel
        fields = ['id', 'manufacturer', 'model', 'monetary_value']

class VentilatorSerializer(serializers.HyperlinkedModelSerializer):
    ventilator_model = VentilatorModelSerializer()
    class Meta:
        model = Ventilator
        fields = ['id', 'quality', 'serial_number', 'ventilator_model', 'status', 'unavailable_status']

    def update(self, instance, validated_data):
        instance.quality = validated_data['quality']
        instance.serial_number = validated_data['serial_number']
        instance.ventilator_model.manufacturer = validated_data['ventilator_model']['manufacturer']
        instance.ventilator_model.model = validated_data['ventilator_model']['model']
        instance.ventilator_model.monetary_value = validated_data['ventilator_model']['monetary_value']
        allowed_statuses_for_edit = [Ventilator.Status.Available.name, Ventilator.Status.Unavailable.name]

        # The only allowed manual state transitions would be:
            # Available to Unavailable (inUse, Broken, needs repair, etc). In this case, we're going to want to decrement the amount 
                # amount offered by the current approved request.
            # Unavailable (PendingOffer) to Unavailable (inUse, Broken, needs Repair). In this case we decrement from current open offer.
            # Unavailable (InUse, Broken, needs repair) to unavailable (pendingOffer): In this case, we update offer.
        new_status = validated_data['status']
        new_unavailable_status = validated_data['unavailable_status']
        if instance.status in allowed_statuses_for_edit and new_status == Ventilator.Status.Unavailable.name:
            if new_unavailable_status != Ventilator.UnavailableReason.PendingOffer.name:
                offer = None
                if instance.status == Ventilator.Status.Available.name:
                    # Decrement from approved offer
                    offer = Offer.objects.filter(is_valid=True).filter(hospital=instance.current_hospital).filter(status=Offer.Status.Approved.name).first()
                else:
                    # Decrement from open offer.
                    offer = Offer.objects.filter(is_valid=True).filter(hospital=instance.current_hospital).filter(status=Offer.Status.Open.name).first()
                offer.offered_qty -= 1
                if offer.offered_qty == 0:
                    offer.status = Offer.Status.Closed.name
                offer.save()
            else:
                if instance.unavailable_status != Ventilator.Status.PendingOffer.name:
                    views.update_offer(instance.current_hospital, instance.updated_by_user)
            instance.status = new_status                
            instance.unavailable_status = new_unavailable_status
        instance.save()
        instance.ventilator_model.save()

        return instance


# class AllocationSerializer(serializer):

#     class Meta:
#         model = Allocation
#         fields = ['id', 'status', 'request', 'offer', 'allocated_qty', 'shipped_qty']

class ShipmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id', 'status', 'tracking_number', 'shipping_service']

    def update(self, instance, validated_data):
      
        # appropriate_status_changes[Shipment.Status.Open.name] = [Shipment.Status.Packed.name, Shipment.Status.Cancelled.name]
        # appropriate_status_changes[Shipment.Status.Packed.name] = [Shipment.Status.Shipped.name, Shipment.Status.Cancelled.name]
        # appropriate_status_changes[Shipment.Status.Shipped.name] = [Shipment.Status.Arrived.name, Shipment.Status.Cancelled.name]
        # appropriate_status_changes[Shipment.Status.Arrived.name] = [Shipment.Status.Accepted.name, Shipment.Status.Cancelled.name]
        # appropriate_status_changes[Shipment.Status.Accepted.name] = [Shipment.Status.RequestedReserve.name, Shipment.Status.Cancelled.name]
        status = validated_data['status']
        instance.status = status
        if status == Shipment.Status.Cancelled.name:
            shipment_ventilators = instance.shipmentventilator_set.all()
            if shipment_ventilators:
                for shipment_ventilator in shipment_ventilators:
                    actual_ventilator = shipment_ventilator.ventilator
                    actual_ventilator.status = Ventilator.Status.Available.name
                    actual_ventilator.unavailable_reason = None
                    actual_ventilator.save()
        elif status == Shipment.Status.Shipped.name:
            instance.tracking_number = validated_data['tracking_number']
            instance.shipping_service = validated_data['shipping_service']
            shipment_ventilators = instance.shipmentventilator_set.all()
            if shipment_ventilators:
                for shipment_ventilator in shipment_ventilators:
                    actual_ventilator = shipment_ventilator.ventilator
                    actual_ventilator.current_hospital = instance.allocation.request.hospital
                    actual_ventilator.status = Ventilator.Status.InTransit.name
                    actual_ventilator.save()
        elif status == Shipment.Status.Accepted.name:
            shipment_ventilators = instance.shipmentventilator_set.all()
            ventilator_count = len(shipment_ventilators)
            reserve_vent_needed = ventilator_count * (SystemParameters.getInstance().destination_reserve / 100)
            reserve_vent_allocated = 0
            if shipment_ventilators:
                for shipment_ventilator in shipment_ventilators:
                    actual_ventilator = shipment_ventilator.ventilator
                    if reserve_vent_allocated < reserve_vent_needed:
                        actual_ventilator.status = Ventilator.Status.DestinationReserve.name
                        reserve_vent_allocated+=1
                    else:
                        actual_ventilator.status = Ventilator.Status.Unavailable.name
                        actual_ventilator.unavailable_status = Ventilator.UnavailableReason.InUse.name
                    actual_ventilator.save()
        instance.save()
        return instance
class SystemParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemParameters
        fields = ['destination_reserve', 'strategic_reserve',
            'reputation_score_weight', 'contribution_weight',
            'projected_load_weight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weight_params = ['reputation_score_weight', 'contribution_weight',
            'projected_load_weight']
        for field in self.fields:
            if field in self.weight_params:
                self.fields[field].section = 'weight'
            else:
                self.fields[field].section = ''

    def validate(self, data):
        for field in self.fields:
            if not field in data.keys():
                raise serializers.ValidationError('All fields are mandatory.')

        sum = functools.reduce(
            lambda a, b: a + data[b],
            self.weight_params,
            0
        )
        if sum != 100.0:
            raise serializers.ValidationError('Weights must add up to 100%.')
        for value in data.values():
            if value < 0.0 or value > 100.0 :
                raise serializers.ValidationError('Parameter values must be in the range [0.0, 100.0]')
        return data


# class SignupSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=100, required=True)
#     email = serializers.EmailField(required=True)
#     user_type = serializers.ChoiceField(
#         choices=[(tag.value, tag.name) for tag in User.UserType],
#         required=True,
#         label='What type of account do you need?')
#     hospital_name = serializers.CharField(max_length=100, required=False, label='Name')
#     hospital_address = serializers.CharField(max_length=100, required=False, label='Address')
#     hospital_within_group_only = serializers.BooleanField(required=False, label='Allow ventilator transfers only within my hospital group?')
#     # hospital_hospitalgroup = serializers.ChoiceField(
#     #     choices=get_hospital_group_choices(),
#     #     required=False,
#     #     label='Hospital Group')
#     supplier_name = serializers.CharField(max_length=100, required=False, label='Name')
#     supplier_address = serializers.CharField(max_length=100, required=False, label='Address')
#     # hospitalgroup_name = serializers.CharField(max_length=100, required=False, label='Name')
#     System_name = serializers.CharField(max_length=100, required=False, label='Name')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # refresh results of query so don't serve stale results
#         self.fields['hospital_hospitalgroup'].choices = get_hospital_group_choices()
#         sections = {}
#         sections[''] = ['username', 'email', 'user_type']
#         sections['Hospital'] = ['hospital_name', 'hospital_address', 'hospital_within_group_only', 'hospital_hospitalgroup']
#         sections['Supplier'] = ['supplier_name', 'supplier_address']
#         # sections['Hospital Group'] = ['hospitalgroup_name']
#         sections['System Operator'] = ['System_name']

#         for section, fields in sections.items():
#             for field in fields:
#                 self.fields[field].section = section

#     def validate(self, data):
#         user_type = data.get('user_type')
#         validate_signup(data, user_type, serializers.ValidationError)
#         return data

#     def save(self):
#         username = self.validated_data.get('username')
#         email = self.validated_data.get('email')
#         user_type = self.validated_data.get('user_type')
#         hospital_name = self.validated_data.get('hospital_name')
#         hospital_address = self.validated_data.get('hospital_address')
#         hospital_within_group_only = self.validated_data.get('within_group_only', False)
#         # hospital_hospitalgroup = self.validated_data.get('hospital_hospitalgroup')
#         supplier_name = self.validated_data.get('supplier_name')
#         supplier_address = self.validated_data.get('supplier_address')
#         hospitalgroup_name = self.validated_data.get('hospitalgroup_name')
#         System_name = self.validated_data.get('System_name')

#         subject = 'Credentials Requested'
#         body = 'username: {username}\nemail: {email}\nuser type: {user_type}\n'.format(username=username, email=email, user_type=user_type)

#         if user_type == User.UserType.Hospital.name:
#             body += 'name: {name}\naddress: {address}\nwithin group only: {within_group_only}\nhospital group: {hospital_group}\n'.format(
#                 name=hospital_name,
#                 address=hospital_address,
#                 within_group_only=hospital_within_group_only,
#                 # hospital_group=HospitalGroup.objects.get(id=hospital_hospitalgroup),
#             )
#         elif user_type == User.UserType.Supplier.name:
#             body += 'name: {name}\naddress: {address}\n'.format(name=supplier_name, address=supplier_address)
#         elif user_type == User.UserType.HospitalGroup.name:
#             body += 'name: {name}\n'.format(name=hospitalgroup_name)
#         elif user_type == User.UserType.System.name:
#             body += 'name: {name}\n'.format(name=System_name)

#         # send email to our email address with signup info
#         send_mail(subject, body, DEFAULT_EMAIL, [DEFAULT_EMAIL], fail_silently=False)
