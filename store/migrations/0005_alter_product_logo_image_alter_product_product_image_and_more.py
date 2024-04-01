# Generated by Django 4.2.11 on 2024-04-01 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_alter_product_logo_image_alter_product_product_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="logo_image",
            field=models.FileField(
                blank=True,
                upload_to="gordegames_post_img",
                verbose_name="Imagem do Logo",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_image",
            field=models.FileField(
                upload_to="gordegames_post_img", verbose_name="Imagem do Produto"
            ),
        ),
        migrations.AlterField(
            model_name="productgallery",
            name="image",
            field=models.FileField(max_length=255, upload_to="gordegames_post_img"),
        ),
    ]
