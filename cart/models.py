from django.db import models
from store.models import Product
from accounts.models import Account
from django.utils.translation import gettext_lazy as _

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True, verbose_name=_('ID do Carrinho'))
    date_added = models.DateField(auto_now_add=True, verbose_name=_('Data de Adição'))

    def __str__(self):
        return self.cart_id

    class Meta:
        verbose_name = _('Carrinho')
        verbose_name_plural = _('Carrinhos')

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, verbose_name=_('Usuário'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Produto'))
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, verbose_name=_('Carrinho'))
    quantity = models.IntegerField(verbose_name=_('Quantidade'))
    is_active = models.BooleanField(default=True, verbose_name=_('Ativo'))

    def subtotal(self):
        if self.product.discount_price:
            theprice = self.product.discount_price * self.quantity
            subtotal_formatted = '{:,.2f}'.format(round(theprice, 2)).replace(',', 'x').replace('.', ',').replace('x', '.')
        else:
            subtotal_formatted = '{:,.2f}'.format(round(self.product.price * self.quantity, 2)).replace(',', 'x').replace('.', ',').replace('x', '.')
        return subtotal_formatted

    def __str__(self):
        return f"{self.product}"

    class Meta:
        verbose_name = _('Item do Carrinho')
        verbose_name_plural = _('Itens do Carrinho')
