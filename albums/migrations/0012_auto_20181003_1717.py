# Generated by Django 2.1 on 2018-10-03 17:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0011_auto_20181003_1531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listenurl',
            name='album',
        ),
        migrations.DeleteModel(
            name='ListenURL',
        ),
    ]