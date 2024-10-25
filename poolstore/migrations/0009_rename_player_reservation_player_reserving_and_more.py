# Generated by Django 5.1.1 on 2024-10-25 13:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poolstore', '0008_matchup_timestamp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reservation',
            old_name='player',
            new_name='player_reserving',
        ),
        migrations.AddField(
            model_name='reservation',
            name='other_player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='poolstore.player'),
        ),
    ]