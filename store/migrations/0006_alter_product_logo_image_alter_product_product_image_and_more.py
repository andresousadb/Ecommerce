# Generated by Django 4.2.11 on 2024-04-01 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_alter_product_logo_image_alter_product_product_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="logo_image",
            field=models.ImageField(
                blank=True, upload_to="imagens/", verbose_name="Imagem do Logo"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_image",
            field=models.ImageField(
                upload_to="imagens/", verbose_name="Imagem do Produto"
            ),
        ),
        migrations.AlterField(
            model_name="productgallery",
            name="image",
            field=models.ImageField(max_length=255, upload_to="imagens/"),
        ),
    ]
