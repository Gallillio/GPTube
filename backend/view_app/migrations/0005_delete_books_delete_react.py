# Generated by Django 5.0 on 2024-03-09 19:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('view_app', '0004_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Books',
        ),
        migrations.DeleteModel(
            name='React',
        ),
    ]
