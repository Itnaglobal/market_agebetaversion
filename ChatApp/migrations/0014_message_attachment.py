# Generated by Django 3.2.6 on 2021-09-13 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChatApp', '0013_auto_20210908_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='files/'),
        ),
    ]
