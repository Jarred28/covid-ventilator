# Generated by Django 3.0.4 on 2020-04-03 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_auto_20200403_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='num_needed',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
