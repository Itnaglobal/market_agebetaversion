# Generated by Django 3.2.6 on 2021-09-01 04:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ChatApp', '0006_chatroom_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='chatroom',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ChatApp.chatroom'),
        ),
    ]
