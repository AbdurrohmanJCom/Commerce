# Generated by Django 4.2.1 on 2023-05-27 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_remove_listing_image_listing_imageurl_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Catagories'},
        ),
        migrations.RenameField(
            model_name='listing',
            old_name='imageUrl',
            new_name='image_url',
        ),
        migrations.AddField(
            model_name='listing',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
