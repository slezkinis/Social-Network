# Generated by Django 4.2.2 on 2024-01-06 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_rename_created_at_message_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_delivered',
            field=models.BooleanField(default=False, verbose_name='Доставлено до получателя'),
        ),
    ]
