# Generated by Django 2.1 on 2018-08-27 21:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('chart', models.IntegerField(blank=True, null=True)),
                ('row', models.IntegerField(blank=True, null=True)),
                ('date_finished', models.DateField(blank=True, null=True)),
                ('time_length', models.DurationField(blank=True, null=True)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('album_art', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='PrimaryGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(blank=True, null=True)),
                ('listen', models.IntegerField(blank=True, null=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='albums.Album')),
            ],
        ),
        migrations.CreateModel(
            name='SubGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='albums', to='albums.Artist'),
        ),
        migrations.AddField(
            model_name='album',
            name='primary_genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='albums.PrimaryGenre'),
        ),
    ]
