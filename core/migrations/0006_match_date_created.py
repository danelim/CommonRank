# Generated by Django 2.0.2 on 2018-02-18 14:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180218_0719'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='date_created',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]