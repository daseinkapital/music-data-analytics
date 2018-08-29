# Generated by Django 2.1 on 2018-08-27 21:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumSubgenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subgenres', to='albums.Album')),
                ('subgenre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='albums', to='albums.SubGenre')),
            ],
        ),
    ]
