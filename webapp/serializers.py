from django.core.mail import send_mail
from rest_framework import serializers
from webapp.models import Ventilator

from covid.settings import EMAIL
from .models import HospitalGroup, User


class VentilatorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ventilator
        fields = ['id', 'model_num']

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    user_type = serializers.ChoiceField(
        choices=[(tag.value, tag.name) for tag in User.UserType],
        required=True,
        label='What type of account do you need?')
    hospital_name = serializers.CharField(max_length=100, required=False, label='Name')
    hospital_address = serializers.CharField(max_length=100, required=False, label='Address')
    hospital_within_group_only = serializers.BooleanField(required=False, label='Allow ventialator transfers only within my hospital group?')
    hospital_hospitalgroup = serializers.ChoiceField(
        choices=[(hg.id, hg.name) for hg in HospitalGroup.objects.all()],
        required=False,
        label='Hospital Group')
    supplier_name = serializers.CharField(max_length=100, required=False, label='Name')
    supplier_address = serializers.CharField(max_length=100, required=False, label='Address')
    hospitalgroup_name = serializers.CharField(max_length=100, required=False, label='Name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sections = {}
        sections['all'] = ['username', 'email', 'user_type']
        sections['Hospital'] = ['hospital_name', 'hospital_address', 'hospital_within_group_only', 'hospital_hospitalgroup']
        sections['Supplier'] = ['supplier_name', 'supplier_address']
        sections['Hospital Group'] = ['hospitalgroup_name']
        for section, fields in sections.items():
            for field in fields:
                self.fields[field].section = section

    def validate(self, data):
        pass

    def save(self):
        username = self.validated_data['username']
        email = self.validated_data['email']
        user_type = self.validated_data['user_type']
        hospital_name = self.validated_data.get('hospital_name', None)
        hospital_address = self.validated_data.get('hospital_address', None)
        hospital_within_group_only = self.validated_data.get('within_group_only', False)
        hospital_hospitalgroup = self.validated_data.get('hospital_hospitalgroup', None)
        supplier_name = self.validated_data.get('supplier_name', None)
        supplier_address = self.validated_data.get('supplier_address', None)
        hospitalgroup_name = self.validated_data.get('hospitalgroup_name', None)

        subject = 'Credentials Requested'
        body = 'username: {username}\nemail: {email}\nuser type: {user_type}\n'.format(username=username, email=email, user_type=user_type)

        if user_type == User.UserTye.Hospital.name:
            body += 'name: {name}\naddress: {address}\nwithin group only: {within_group_only}\n hospital group: {hospital_group}\n'.format(
                name=hospital_name,
                address=hospital_address,
                within_group_only=hospital_within_group_only,
                hospital_group=hospital_hospitalgroup,
            )
        elif user_type == User.UserType.Supplier.name:
            body += 'name: {name}\naddress: {address}\n'.format(name=supplier_name, address=supplier_address)
        elif user_type == User.UserType.HospitalGroup.name:
            body += 'name: {name}\n'

        # send email to our email address with signup info
        send_mail(subject, body, EMAIL, EMAIL, fail_silently=False)
