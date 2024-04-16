from io import BytesIO

from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

class Product(models.Model):
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE, verbose_name=_('Categoria'))
    name = models.CharField(max_length=200, unique=True, verbose_name=_('Nome'))
    brand_name = models.CharField(max_length=30, blank=True, verbose_name=_('Marca'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Slug'))
    description = models.TextField(max_length=255, verbose_name=_('Descrição'))
    price = models.DecimalField(
        verbose_name=_('Preço regular'),
        help_text=_('Máximo 99999.99'),
        error_messages={
            'name': {
                'max_length': _('O preço deve estar entre 0 e 999.999,99.'),
            },
        },
        max_digits=7,
        decimal_places=2,
    )
    discount_percentage = models.IntegerField(default=0, blank=True, verbose_name=_('Porcentagem de desconto'))
    product_image = models.ImageField(upload_to='imagens/', verbose_name=_('Imagem do Produto'), max_length=255)
    alt_text = models.CharField(max_length=200, verbose_name=_('Texto alternativo'))
    stock = models.IntegerField(verbose_name=_('Estoque'))
    is_available = models.BooleanField(default=True, verbose_name=_('Disponível'))
    is_trending = models.BooleanField(default=False, verbose_name=_('Tendência'))
    logo_altText = models.CharField(max_length=200, blank=True, verbose_name=_('Texto alternativo do Logo'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))
    views_count = models.IntegerField(default=0)  # Adicionando campo para contar visualizações

    def save(self, *args, **kwargs):
        # Chamar o método save do modelo
        super().save(*args, **kwargs)

        if self.product_image:
            # Abrir a imagem a partir do armazenamento padrão do Django
            with default_storage.open(self.product_image.name, 'rb') as image_file:
                # Ler a imagem do arquivo
                img = Image.open(image_file)
                # Redimensionar
                img_resized = img.resize((500, 500))

                # Salvar a imagem redimensionada em um buffer de bytes
                img_buffer = BytesIO()
                img_resized.save(img_buffer, format='JPEG')
                img_buffer.seek(0)

                # Salvar o arquivo redimensionado no mesmo caminho e nome do arquivo original no S3
                default_storage.delete(self.product_image.name)  # Exclui a imagem original
                default_storage.save(self.product_image.name, ContentFile(img_buffer.getvalue()))

    def discountPrice(self):
        if self.discount_percentage > 0:
            theprice = self.price - ((self.price * self.discount_percentage) / 100)
            return round(theprice, 2)
    discount_price = property(discountPrice)

    def average_rating(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = int(reviews['average'])
        return avg

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.name

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=300, blank=True)
    rating = models.IntegerField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject