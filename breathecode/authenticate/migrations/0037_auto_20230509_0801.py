# Generated by Django 3.2.19 on 2023-05-09 08:01

import breathecode.utils.validators.language
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0036_githubacademyuserlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.CharField(
                blank=True,
                help_text=
                'User biography, this will be used the bio in the lang of the user, otherwise frontend will usethe Profile translation',
                max_length=255,
                null=True),
        ),
        migrations.CreateModel(
            name='ProfileTranslation',
            fields=[
                ('id',
                 models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang',
                 models.CharField(
                     help_text='ISO 639-1 language code + ISO 3166-1 alpha-2 country code, e.g. en-US',
                     max_length=5,
                     unique=True,
                     validators=[breathecode.utils.validators.language.validate_language_code])),
                ('bio',
                 models.CharField(
                     help_text=
                     'User biography, this will be used the bio in the lang of the user, otherwise frontend will usethe Profile translation',
                     max_length=255)),
                ('profile',
                 models.ForeignKey(help_text='Profile',
                                   on_delete=django.db.models.deletion.CASCADE,
                                   to='authenticate.profile')),
            ],
        ),
    ]