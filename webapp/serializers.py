import functools

from django.core.mail import send_mail
from rest_framework import serializers

from .models import HospitalGroup, SystemParameters, Ventilator, VentilatorModel, User
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
        fields = ['id', 'quality', 'serial_number', 'ventilator_model']

    def update(self, instance, validated_data):
        instance.quality = validated_data['quality']
        instance.serial_number = validated_data['serial_number']
        instance.ventilator_model.manufacturer = validated_data['ventilator_model']['manufacturer']
        instance.ventilator_model.model = validated_data['ventilator_model']['model']
        instance.ventilator_model.monetary_value = validated_data['ventilator_model']['monetary_value']

        instance.save()
        instance.ventilator_model.save()

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
