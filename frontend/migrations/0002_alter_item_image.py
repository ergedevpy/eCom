# Generated by Django 4.1.1 on 2022-09-30 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, upload_to='items/%Y/%m/%d/'),
        ),
    ]
