# Generated by Django 3.0.4 on 2020-04-15 08:30

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import webapp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('inserted_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_updated_by_user', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Approved', 'Approved'), ('Cancelled', 'Cancelled'), ('Closed', 'Closed')], default=webapp.models.Allocation.Status['Open'], max_length=100)),
                ('allocated_qty', models.IntegerField()),
                ('shipped_qty', models.IntegerField(default=0)),
                ('opened_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='allocation_approved_by_user', to=settings.AUTH_USER_MODEL)),
                ('cancelled_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='allocation_cancelled_by_user', to=settings.AUTH_USER_MODEL)),
                ('closed_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='allocation_closed_by_user', to=settings.AUTH_USER_MODEL)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='allocation_inserted_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('reputation_score', models.FloatField(blank=True, null=True)),
                ('within_group_only', models.BooleanField(default=False)),
                ('contribution', models.IntegerField(default=0)),
                ('projected_load', models.IntegerField(default=0)),
                ('current_load', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HospitalGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='hospitalgroup_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='hospitalgroup_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Packed', 'Packed'), ('Shipped', 'Shipped'), ('Arrived', 'Arrived'), ('Accepted', 'Accepted'), ('RequestedReserve', 'RequestedReserve'), ('Cancelled', 'Cancelled'), ('Closed', 'Closed')], default=webapp.models.Shipment.Status['Open'], max_length=100)),
                ('shipped_qty', models.IntegerField(default=0)),
                ('opened_at', models.DateTimeField(auto_now_add=True)),
                ('packed_at', models.DateTimeField(blank=True, null=True)),
                ('shipped_at', models.DateTimeField(blank=True, null=True)),
                ('arrived_at', models.DateTimeField(blank=True, null=True)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('accepted_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_accepted_by_user', to=settings.AUTH_USER_MODEL)),
                ('allocation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.Allocation')),
                ('arrived_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_arrived_by_user', to=settings.AUTH_USER_MODEL)),
                ('cancelled_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_cancelled_by_user', to=settings.AUTH_USER_MODEL)),
                ('closed_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_closed_by_user', to=settings.AUTH_USER_MODEL)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('opened_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('packed_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_packed_by_user', to=settings.AUTH_USER_MODEL)),
                ('shipped_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_shipped_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='supplier_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('name', models.CharField(default='System', max_length=100)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='system_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='system_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VentilatorModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('manufacturer', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('monetary_value', models.IntegerField(default=10000)),
                ('image', models.CharField(blank=True, max_length=200, null=True)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='ventilatormodel_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='ventilatormodel_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ventilator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Unknown', 'Unknown'), ('Available', 'Available'), ('InUse', 'In Use'), ('InTransit', 'In Transit'), ('SourceReserve', 'Source Reserve'), ('DestinationReserve', 'Destination Reserve')], default=webapp.models.Ventilator.Status['Unknown'], max_length=100)),
                ('monetary_value', models.IntegerField()),
                ('image', models.CharField(blank=True, max_length=200, null=True)),
                ('quality', models.IntegerField(blank=True, null=True)),
                ('current_hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ventilator_current_hospital', to='webapp.Hospital')),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='ventilator_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('last_shipment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipment_last_shipment', to='webapp.Shipment')),
                ('owning_hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ventilator_owning_hospital', to='webapp.Hospital')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Supplier')),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='ventilator_updated_by_user', to=settings.AUTH_USER_MODEL)),
                ('ventilator_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.VentilatorModel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('user_role', models.CharField(choices=[('Admin', 'Admin'), ('Manager', 'Manager'), ('Operator', 'Operator'), ('Shipper', 'Shipper'), ('NoRole', 'NoRole')], max_length=100)),
                ('assigned_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_role_user', to=settings.AUTH_USER_MODEL)),
                ('granted_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_role_granted_by_user', to=settings.AUTH_USER_MODEL)),
                ('hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Hospital')),
                ('hospital_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.HospitalGroup')),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='userrole_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Supplier')),
                ('system', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.System')),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='userrole_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemParameters',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('destination_reserve', models.FloatField(default=0.0)),
                ('strategic_reserve', models.FloatField(default=0.0)),
                ('reputation_score_weight', models.FloatField(default=34.0)),
                ('contribution_weight', models.FloatField(default=33.0)),
                ('projected_load_weight', models.FloatField(default=33.0)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='systemparameters_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='systemparameters_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='system',
            name='users',
            field=models.ManyToManyField(through='webapp.UserRole', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='supplier',
            name='users',
            field=models.ManyToManyField(through='webapp.UserRole', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ShipmentVentilator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='shipmentventilator_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.Shipment')),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='shipmentventilator_updated_by_user', to=settings.AUTH_USER_MODEL)),
                ('ventilator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.Ventilator')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Approved', 'Approved'), ('Cancelled', 'Cancelled'), ('Closed', 'Closed')], default=webapp.models.Request.Status['Open'], max_length=100)),
                ('requested_qty', models.IntegerField()),
                ('allocated_qty', models.IntegerField(default=0)),
                ('shipped_qty', models.IntegerField(default=0)),
                ('opened_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='request_approved_by_user', to=settings.AUTH_USER_MODEL)),
                ('cancelled_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='request_cancelled_by_user', to=settings.AUTH_USER_MODEL)),
                ('closed_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='request_closed_by_user', to=settings.AUTH_USER_MODEL)),
                ('hospital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.Hospital')),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='request_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('opened_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='request_opened_by_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='request_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inserted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_valid', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('Approved', 'Approved'), ('Replaced', 'Replaced'), ('Cancelled', 'Cancelled'), ('Closed', 'Closed')], default=webapp.models.Offer.Status['Open'], max_length=100)),
                ('requested_qty', models.IntegerField()),
                ('allocated_qty', models.IntegerField(default=0)),
                ('shipped_qty', models.IntegerField(default=0)),
                ('opened_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('replaced_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offer_approved_by_user', to=settings.AUTH_USER_MODEL)),
                ('cancelled_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offer_cancelled_by_user', to=settings.AUTH_USER_MODEL)),
                ('closed_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offer_closed_by_user', to=settings.AUTH_USER_MODEL)),
                ('hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Hospital')),
                ('inserted_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='offer_inserted_by_user', to=settings.AUTH_USER_MODEL)),
                ('opened_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='offer_opened_by_user', to=settings.AUTH_USER_MODEL)),
                ('replaced_by_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offer_replaced_by_user', to=settings.AUTH_USER_MODEL)),
                ('requests', models.ManyToManyField(through='webapp.Allocation', to='webapp.Request')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.Supplier')),
                ('updated_by_user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='offer_updated_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='hospitalgroup',
            name='users',
            field=models.ManyToManyField(through='webapp.UserRole', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hospital',
            name='hospital_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.HospitalGroup'),
        ),
        migrations.AddField(
            model_name='hospital',
            name='inserted_by_user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='hospital_inserted_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hospital',
            name='updated_by_user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='hospital_updated_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hospital',
            name='users',
            field=models.ManyToManyField(through='webapp.UserRole', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='allocation',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.Offer'),
        ),
        migrations.AddField(
            model_name='allocation',
            name='opened_by_user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='allocation_opened_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='allocation',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.Request'),
        ),
        migrations.AddField(
            model_name='allocation',
            name='updated_by_user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='allocation_updated_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('assigned_user', 'system'), name='user_system_uq'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('assigned_user', 'hospital'), name='user_hospital_uq'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('assigned_user', 'hospital_group'), name='user_hospital_group_uq'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('assigned_user', 'supplier'), name='user_supplier_uq'),
        ),
        migrations.AddConstraint(
            model_name='shipmentventilator',
            constraint=models.UniqueConstraint(fields=('shipment', 'ventilator'), name='shipment_ventilator_uq'),
        ),
    ]
