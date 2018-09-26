# Generated by Django 2.1 on 2018-09-24 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0008_auto_20180913_0327'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumArtist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_artists', to='albums.Album')),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_albums', to='albums.Artist')),
            ],
        ),
        migrations.AlterModelOptions(
            name='rating',
            options={'ordering': ['-listen']},
        ),
        migrations.AddField(
            model_name='recommendation',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='rating',
            name='album',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ratings', to='albums.Album'),
        ),
    ]