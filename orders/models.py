from django.db import models
from accounts.models import Account
from store.models import Product


class Order(models.Model):
    STATUS = (
        ('Orçamento', 'Orçamento'),
        ('Aceito', 'Aceito'),
        ('Cancelado', 'Cancelado'),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    f_name = models.CharField(max_length=50)
    l_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    tel = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_total = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def full_name(self):
        return f"{self.f_name} {self.l_name}"

    def thecountry(self):
        if self.country:
            return f"{self.country}, {self.state}, {self.city}"
        else:
             return f"{self.state}, {self.city}"

    def __str__(self):
        return self.f_name

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name


