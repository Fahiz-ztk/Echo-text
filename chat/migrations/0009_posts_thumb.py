# Generated by Django 5.0.3 on 2024-07-14 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_groupmessages_msgtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='thumb',
            field=models.ImageField(blank=True, null=True, upload_to='chat/statics/thumb'),
        ),
    ]
