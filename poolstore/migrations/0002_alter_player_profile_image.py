# Generated by Django 5.1.3 on 2024-11-13 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poolstore', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='profile_image',
            field=models.ImageField(null=True, upload_to='profile-pics'),
        ),
    ]
