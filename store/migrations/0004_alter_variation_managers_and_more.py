# Generated by Django 4.0.6 on 2022-07-29 19:39

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_variations_variation'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='variation',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RenameField(
            model_name='variation',
            old_name='Variation_category',
            new_name='variation_category',
        ),
    ]
