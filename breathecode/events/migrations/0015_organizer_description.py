# Generated by Django 3.1.2 on 2020-10-12 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_organizer'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizer',
            name='description',
            field=models.CharField(blank=True,
                                   default=None,
                                   max_length=250,
                                   null=True),
        ),
    ]
