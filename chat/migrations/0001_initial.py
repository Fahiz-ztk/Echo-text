# Generated by Django 5.0.3 on 2024-06-17 15:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=200)),
                ('pfp', models.ImageField(null=True, upload_to='chat/statics/pfp')),
                ('bio', models.CharField(max_length=500)),
                ('status', models.CharField(max_length=20)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(max_length=50, null=True)),
                ('image', models.ImageField(null=True, upload_to='chat/statics/posts')),
                ('date', models.DateField(auto_now_add=True, null=True)),
                ('time', models.TimeField(auto_now_add=True, null=True)),
                ('likes', models.ManyToManyField(related_name='likes', to='chat.userdetails')),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.userdetails')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=300, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='chat/statics/messages')),
                ('time', models.TimeField(auto_now_add=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('reader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reader', to='chat.userdetails')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer', to='chat.userdetails')),
            ],
        ),
    ]
