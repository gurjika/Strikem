# Generated by Django 5.1.3 on 2024-11-21 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poolstore', '0007_alter_notification_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchup',
            name='read',
            field=models.BooleanField(default=True),
        ),
    ]
