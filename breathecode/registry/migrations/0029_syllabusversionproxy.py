# Generated by Django 3.2.16 on 2023-03-28 04:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0056_auto_20230317_1657'),
        ('registry', '0028_alter_asset_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyllabusVersionProxy',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('admissions.syllabusversion', ),
        ),
    ]
