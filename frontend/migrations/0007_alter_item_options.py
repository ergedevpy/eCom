# Generated by Django 4.1.1 on 2022-10-01 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0006_alter_item_image"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="item",
            options={"ordering": ["-id"]},
        ),
    ]
