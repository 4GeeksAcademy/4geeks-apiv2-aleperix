# Generated by Django 3.1.2 on 2020-10-29 06:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0011_auto_20201006_0058'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authenticate', '0011_auto_20201029_0634'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileAcademy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('academy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admissions.academy')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
