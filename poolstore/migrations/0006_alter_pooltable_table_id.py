# Generated by Django 5.1.1 on 2024-10-25 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poolstore', '0005_pooltable_table_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pooltable',
            name='table_id',
            field=models.IntegerField(null=True),
        ),
    ]
