# Generated by Django 3.0.4 on 2020-04-09 21:08

from django.db import migrations, models
import webapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ventilator',
            name='state',
            field=models.CharField(choices=[('Available', 'Available'), ('Requested', 'Requested'), ('InTransit', 'InTransit'), ('InUse', 'InUse'), ('Reserve', 'Reserve'), ('RequestedReserve', 'RequestedReserve'), ('SourceReserve', 'SourceReserve')], default=webapp.models.Ventilator.State['Available'], max_length=100),
        ),
    ]
