from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string

from .forms import CovidUserCreationForm
from .models import Hospital, HospitalGroup, Supplier, SystemOperator, User

class HospitalInline(admin.StackedInline):
    model = Hospital
    verbose_name_plural = 'Hospital'

class SupplierInline(admin.StackedInline):
    model = Supplier
    verbose_name_plural = 'Supplier'

class HospitalGroupInline(admin.StackedInline):
    model = HospitalGroup
    verbose_name_plural = 'Hospital Group'

class SystemOperatorInline(admin.StackedInline):
    model = SystemOperator
    verbose_name_plural = 'System Operator'


class CovidUserAdmin(UserAdmin):
    add_form = CovidUserCreationForm
    inlines = (HospitalGroupInline, HospitalInline, SupplierInline, SystemOperatorInline)

    add_fieldsets = (
        (None, {
            'description': 'Enter name and email address. They will receive an email to set their password.',
            'fields': ('username', 'email', 'user_type'),
        }),
        ('Password', {
            'description': 'Optionally you may set the password here.',
            'fields': ('password1', 'password2'),
            'classes': ('collapse', 'collapse-closed'),
        }),
        ('Hospital Group', {
            'description': 'Only fill out this section if the user represents a hospital group.',
            'fields': ('hospitalgroup_name',),
            'classes': ('collapse', 'collapse-closed'),
        }),
        ('Hospital', {
            'description': 'Only fill out this section if the user represents a hospital.',
            'fields': ('hospital_name', 'hospital_address', 'hospital_within_group_only', 'hospital_hospitalgroup'),
            'classes': ('collapse', 'collapse-closed'),
        }),
        ('Supplier', {
            'description': 'Only fill out this section if the user represents a supplier.',
            'fields': ('supplier_name', 'supplier_address'),
            'classes': ('collapse', 'collapse-closed'),
        }),
        ('System Operator', {
            'description': 'Only fill out this section if the user is a system operator.',
            'fields': ('systemoperator_name',),
            'classes': ('collapse', 'collapse-closed'),
        }),
    )


    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        if not change and (not form.cleaned_data['password1'] or not obj.has_usable_password()):
            # Django's PasswordResetForm won't let us reset an unusable
            # password. We set it above super() so we don't have to save twice.
            obj.set_password(get_random_string())
            reset_password = True
        else:
            reset_password = False

        super().save_model(request, obj, form, change)

        user_type = form.cleaned_data['user_type']
        hospital_name = form.cleaned_data.get('hospital_name', None)
        hospital_address = form.cleaned_data.get('hospital_address', None)
        hospital_within_group_only = form.cleaned_data.get('hospital_within_group_only', None)
        hospital_hospitalgroup = form.cleaned_data.get('hospital_hospitalgroup', None)
        supplier_name = form.cleaned_data.get('supplier_name', None)
        supplier_address = form.cleaned_data.get('supplier_address', None)
        hospitalgroup_name = form.cleaned_data.get('hospitalgroup_name', None)
        systemoperator_name = form.cleaned_data.get('systemoperator_name', None)

        if user_type == User.UserType.Hospital.name:
            Hospital(
                name=hospital_name,
                address=hospital_address,
                user=obj,
                within_group_only=hospital_within_group_only,
                hospital_group=HospitalGroup.objects.get(id=hospital_hospitalgroup)
            ).save()
        if user_type == User.UserType.Supplier.name:
            Supplier(name=supplier_name, address=supplier_address, user=obj).save()
        if user_type == User.UserType.HospitalGroup.name:
            HospitalGroup(name=hospitalgroup_name, user=obj).save()
        if user_type == User.UserType.SystemOperator.name:
            SystemOperator(name=systemoperator_name, user=obj).save()

        if reset_password:
            reset_form = PasswordResetForm({'email': form.cleaned_data['email']})
            assert reset_form.is_valid()
            reset_form.save(
                request=request,
                use_https=request.is_secure(),
            )

admin.site.register(User, CovidUserAdmin)
