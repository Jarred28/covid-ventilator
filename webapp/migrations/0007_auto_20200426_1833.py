# Generated by Django 3.0.4 on 2020-04-26 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0006_shipment_is_requisition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='status',
            field=models.CharField(choices=[('Open', 'Open'), ('Approved', 'Approved'), ('Packed', 'Packed'), ('Shipped', 'Shipped'), ('Arrived', 'Arrived'), ('Accepted', 'Accepted'), ('RequestedReserve', 'RequestedReserve'), ('Cancelled', 'Cancelled'), ('Closed', 'Closed')], default='Open', max_length=100),
        ),
    ]
