# Generated by Django 2.1 on 2018-08-28 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0002_albumsubgenre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='score',
            field=models.DecimalField(decimal_places=1, max_digits=4, null=True),
        ),
    ]