# Generated by Django 3.0.4 on 2020-04-24 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_auto_20200422_0017'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='is_requisition',
            field=models.BooleanField(default=False),
        ),
    ]
