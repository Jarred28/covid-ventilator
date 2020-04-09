from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string

from .models import HospitalGroup, User
from .utilities import get_hospital_group_choices
from .validation import validate_signup


class CovidUserCreationForm(UserCreationForm):
    hospital_name = forms.CharField(max_length=100, required=False, label='Name')
    hospital_address = forms.CharField(max_length=100, required=False, label='Address')
    hospital_within_group_only = forms.BooleanField(required=False, label='Allow ventialator transfers only within my hospital group?')
    # hospital_hospitalgroup = forms.ChoiceField(
    #     choices=get_hospital_group_choices(),
    #     required=False,
    #     label='Hospital Group')
    supplier_name = forms.CharField(max_length=100, required=False, label='Name')
    supplier_address = forms.CharField(max_length=100, required=False, label='Address')
    hospitalgroup_name = forms.CharField(max_length=100, required=False, label='Name')
    systemoperator_name = forms.CharField(max_length=100, required=False, label='Name')

    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'hospitalgroup_name',
            'hospital_name', 'hospital_address', 'hospital_within_group_only',
            'supplier_name', 'supplier_address',
            'password1', 'password2', 'systemoperator_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.fields['user_type'].required = True
        # need to refresh the choices so don't have stale results
        self.fields['hospital_hospitalgroup'].choices = get_hospital_group_choices()

    def clean(self):
        data = self.cleaned_data
        user_type = self.cleaned_data.get('user_type')
        validate_signup(data, user_type, forms.ValidationError)
