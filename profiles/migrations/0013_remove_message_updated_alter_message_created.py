# Generated by Django 4.2.2 on 2023-12-22 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_alter_message_created_alter_message_updated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='updated',
        ),
        migrations.AlterField(
            model_name='message',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
