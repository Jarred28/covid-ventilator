# Generated by Django 3.0.4 on 2020-03-28 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemParameters',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination_reserve', models.FloatField(default=0.0)),
                ('strategic_reserve', models.FloatField(default=0.0)),
                ('reputation_score_weight', models.FloatField(default=34.0)),
                ('contribution_weight', models.FloatField(default=33.0)),
                ('projected_load_weight', models.FloatField(default=33.0)),
            ],
        ),
        migrations.AddField(
            model_name='hospital',
            name='contribution',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='hospital',
            name='projected_load',
            field=models.IntegerField(default=0),
        ),
    ]
