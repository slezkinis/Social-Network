# Generated by Django 4.2.2 on 2023-12-22 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_rename_created_message_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='created_at',
            new_name='created',
        ),
    ]
