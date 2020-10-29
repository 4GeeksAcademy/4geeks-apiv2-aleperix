# Generated by Django 3.1.2 on 2020-10-29 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0013_slackteam_academy'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackteam',
            name='id',
            field=models.AutoField(auto_created=True, default=None, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='slackteam',
            name='slack_id',
            field=models.CharField(max_length=50),
        ),
    ]
