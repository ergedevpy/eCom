# Generated by Django 4.1.1 on 2022-10-01 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0005_alter_item_discount_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="image",
            field=models.ImageField(
                blank=True, default="images.jpeg", upload_to="items/%Y/%m/%d/"
            ),
        ),
    ]
