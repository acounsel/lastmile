# Generated by Django 3.0.5 on 2020-04-22 22:46

from django.db import migrations, models
import django_lastmile.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('lastmile', '0009_attachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(blank=True, null=True, storage=django_lastmile.storage_backends.PrivateMediaStorage(), upload_to='files/'),
        ),
    ]