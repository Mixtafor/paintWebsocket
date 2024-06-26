# Generated by Django 4.1.5 on 2023-06-20 12:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(max_length=255, unique=True)),
                ('members', models.ManyToManyField(related_name='rooms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
