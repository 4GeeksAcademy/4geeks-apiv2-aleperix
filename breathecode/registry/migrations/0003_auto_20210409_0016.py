# Generated by Django 3.1.6 on 2021-04-09 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0002_auto_20210408_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='difficulty',
            field=models.CharField(blank=True,
                                   choices=[('BEGINNER', 'Beginner'),
                                            ('EASY', 'Easy')],
                                   default=None,
                                   max_length=20,
                                   null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='graded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='asset',
            name='intro_video_url',
            field=models.URLField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='readme',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='readme_url',
            field=models.URLField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='solution_video_url',
            field=models.URLField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='duration',
            field=models.IntegerField(blank=True,
                                      default=None,
                                      help_text='In hours',
                                      null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='lang',
            field=models.CharField(blank=True, default='en', max_length=50),
        ),
    ]
