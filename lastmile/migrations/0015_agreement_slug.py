# Generated by Django 3.0.5 on 2020-05-13 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lastmile', '0014_agreement_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='agreement',
            name='slug',
            field=models.SlugField(blank=True, max_length=255),
        ),
    ]
