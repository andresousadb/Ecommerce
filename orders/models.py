from django.db import models
from accounts.models import Account
from store.models import Product
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    STATUS = (
        ('Orçamento', _('Orçamento')),
        ('Aceito', _('Aceito')),
        ('Cancelado', _('Cancelado')),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20, verbose_name=_('Número do Pedido'))
    f_name = models.CharField(max_length=50, verbose_name=_('Nome'))
    l_name = models.CharField(max_length=50, verbose_name=_('Sobrenome'))
    email = models.EmailField(max_length=100, verbose_name=_('Email'))
    tel = models.CharField(max_length=50, verbose_name=_('Telefone'))
    city = models.CharField(max_length=50, verbose_name=_('Cidade'))
    order_total = models.FloatField(verbose_name=_('Total do Pedido'))
    status = models.CharField(max_length=10, choices=STATUS, default='Orçamento', verbose_name=_('Status'))
    ip = models.CharField(blank=True, max_length=20, verbose_name=_('IP'))
    is_ordered = models.BooleanField(default=False, verbose_name=_('Pedido Realizado'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    def full_name(self):
        return f"{self.f_name} {self.l_name}"

    def thecountry(self):
        if self.country:
            return f"{self.country}, {self.state}, {self.city}"
        else:
            return f"{self.state}, {self.city}"

    def __str__(self):
        return self.f_name

    class Meta:
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_('Pedido'))
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_('Usuário'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Produto'))
    quantity = models.IntegerField(verbose_name=_('Quantidade'))
    product_price = models.FloatField(verbose_name=_('Preço do Produto'))
    ordered = models.BooleanField(default=False, verbose_name=_('Pedido Realizado'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _('Produto do Pedido')
        verbose_name_plural = _('Produtos do Pedido')


