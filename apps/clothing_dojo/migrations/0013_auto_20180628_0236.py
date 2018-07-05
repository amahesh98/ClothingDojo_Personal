# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-28 02:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clothing_dojo', '0012_user_cohort'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='clothing_dojo.User'),
        ),
        migrations.AlterField(
            model_name='user',
            name='cohort',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='clothing_admin.Cohort'),
        ),
    ]
