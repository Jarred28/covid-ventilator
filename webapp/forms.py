from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string

from .models import HospitalGroup, User
from .validation import validate_signup

class CovidUserCreationForm(UserCreationForm):
    hospital_name = forms.CharField(max_length=100, required=False, label='Name')
    hospital_address = forms.CharField(max_length=100, required=False, label='Address')
    hospital_within_group_only = forms.BooleanField(required=False, label='Allow ventialator transfers only within my hospital group?')
    hospital_hospitalgroup = forms.ChoiceField(
        choices=[(hg.id, hg.name) for hg in HospitalGroup.objects.all()],
        required=False,
        label='Hospital Group')
    supplier_name = forms.CharField(max_length=100, required=False, label='Name')
    supplier_address = forms.CharField(max_length=100, required=False, label='Address')
    hospitalgroup_name = forms.CharField(max_length=100, required=False, label='Name')
    systemoperator_name = forms.CharField(max_length=100, required=False, label='Name')

    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'hospitalgroup_name',
            'hospital_name', 'hospital_address', 'hospital_within_group_only',
            'hospital_hospitalgroup', 'supplier_name', 'supplier_address',
            'password1', 'password2', 'systemoperator_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.fields['user_type'].required = True

    def clean(self):
        data = self.cleaned_data
        user_type = self.cleaned_data.get('user_type', None)
        required_fields = {}
        required_fields[User.UserType.Hospital.name] = ['hospital_name', 'hospital_address']
        required_fields[User.UserType.Supplier.name] = ['supplier_name', 'supplier_address']
        required_fields[User.UserType.HospitalGroup.name] = ['hospitalgroup_name']
        required_fields[User.UserType.SystemOperator.name] = ['systemoperator_name']

        validate_signup(data, user_type, required_fields, forms.ValidationError)
