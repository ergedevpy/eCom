# Generated by Django 4.1.1 on 2022-10-05 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0011_item_url_alter_item_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="item",
            old_name="url",
            new_name="item_url",
        ),
    ]
