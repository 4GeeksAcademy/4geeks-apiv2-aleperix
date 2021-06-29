# Generated by Django 3.0.7 on 2020-06-19 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0008_auto_20200619_0214'),
    ]

    operations = [
        migrations.AddField(
            model_name='formentry',
            name='tags',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='client_comments',
            field=models.CharField(blank=True,
                                   default=None,
                                   max_length=250,
                                   null=True),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='location',
            field=models.CharField(blank=True,
                                   default=None,
                                   max_length=20,
                                   null=True),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='referral_key',
            field=models.CharField(blank=True,
                                   default=None,
                                   max_length=50,
                                   null=True),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='utm_campaign',
            field=models.CharField(blank=True,
                                   default=None,
                                   max_length=50,
                                   null=True),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='utm_medium',
            field=models.CharField(blank=True,
                                   default=None,
                                   max_length=50,
                                   null=True),
        ),
    ]
