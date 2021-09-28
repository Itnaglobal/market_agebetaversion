# Generated by Django 3.2.6 on 2021-09-01 04:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ChatApp', '0007_alter_message_chatroom'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroom',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='user',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='welcome_msg',
        ),
        migrations.RemoveField(
            model_name='message',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='message',
            name='messages',
        ),
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.AddField(
            model_name='chatroom',
            name='buyer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='room_name',
            field=models.CharField(max_length=210, null=True),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='sellers',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sellers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
