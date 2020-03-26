from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string

from django.forms.models import inlineformset_factory

from .models import HospitalGroup, User

class CovidUserCreationForm(UserCreationForm):
    hospital_name = forms.CharField(max_length=100, required=False, label='Name')
    hospital_address = forms.CharField(max_length=100, required=False, label='Address')
    hospital_within_group_only = forms.BooleanField(required=False, label='Allow ventialator transfers only within my hospital group?')
    hospital_hospitalgroup = forms.ChoiceField(choices=[(hg.id, hg.name) for hg in HospitalGroup.objects.all()], required=False, label='Hospital Group')
    supplier_name = forms.CharField(max_length=100, required=False, label='Name')
    supplier_address = forms.CharField(max_length=100, required=False, label='Address')
    hospitalgroup_name = forms.CharField(max_length=100, required=False, label='Name')

    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'hospitalgroup_name',
            'hospital_name', 'hospital_address', 'hospital_within_group_only',
            'hospital_hospitalgroup', 'supplier_name', 'supplier_address',
            'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.fields['user_type'].required = True

    def clean(self):
        user_type = self.cleaned_data.get('user_type', None)
        no_hname = self.cleaned_data.get('hospital_name', '') == ''
        no_haddr = self.cleaned_data.get('hospital_address', '') == ''
        no_sname = self.cleaned_data.get('supplier_name', '') == ''
        no_saddr = self.cleaned_data.get('supplier_address', '') == ''
        if not user_type:
            return
        if user_type == User.UserType.Hospital.name and (no_hname or no_haddr):
            raise forms.ValidationError('Hospital information must be provided.')
        if user_type == User.UserType.Supplier.name and (no_sname or no_saddr):
            raise forms.ValidationError('Supplier information must be provided.')

        if user_type == User.UserType.Hospital.name and (not no_sname or not no_saddr):
            raise forms.ValidationError('Only hospital information should be provided.')
        if user_type == User.UserType.Supplier.name and (not no_hname or not no_haddr):
            raise forms.ValidationError('Only supplier information should be provided.')
