# Generated by Django 2.2.10 on 2020-02-24 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lastmile', '0004_action_status_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='commitment',
            name='status_description',
            field=models.TextField(blank=True),
        ),
    ]
