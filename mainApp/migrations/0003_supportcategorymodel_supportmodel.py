# Generated by Django 3.2.6 on 2021-09-16 07:51

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainApp', '0002_auto_20210912_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportCategoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=220)),
            ],
        ),
        migrations.CreateModel(
            name='SupportModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('support_ticket', models.CharField(max_length=220)),
                ('description', models.TextField()),
                ('attachment', models.FileField(blank=True, null=True, upload_to='files/', validators=[django.core.validators.FileExtensionValidator(['pdf'], ['docx'], ['txt'])])),
                ('image_attachment', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('support_status', models.CharField(blank=True, choices=[('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('SOLEV', 'SOLVED')], max_length=220, null=True)),
                ('subject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainApp.supportcategorymodel')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
