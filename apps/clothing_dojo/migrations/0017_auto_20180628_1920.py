# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-28 19:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothing_dojo', '0016_auto_20180628_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='size',
            field=models.CharField(default='-', max_length=3),
        ),
    ]
