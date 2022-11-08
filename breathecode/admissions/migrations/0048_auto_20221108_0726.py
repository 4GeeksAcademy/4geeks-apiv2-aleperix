# Generated by Django 3.2.16 on 2022-11-08 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        ('admissions', '0047_merge_20220924_0611'),
    ]

    operations = [
        migrations.AddField(
            model_name='academy',
            name='allowed_currencies',
            field=models.ManyToManyField(related_name='academies', to='payments.Currency'),
        ),
        migrations.AddField(
            model_name='academy',
            name='main_currency',
            field=models.ForeignKey(blank=True,
                                    null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='+',
                                    to='payments.currency'),
        ),
    ]
