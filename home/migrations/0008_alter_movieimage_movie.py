# Generated by Django 4.1.7 on 2023-04-03 20:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_rename_movie_id_movie_mov_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movieimage',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='home.movie'),
        ),
    ]