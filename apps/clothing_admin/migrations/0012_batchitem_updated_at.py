# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-28 22:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothing_admin', '0011_batch_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
