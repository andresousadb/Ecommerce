from .models import  Order, OrderProduct
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html



class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product_price', 'quantity', 'ordered')
    extra = 0
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'tel', 'email', 'order_total', 'created_at', 'status', 'approve_button')

    def approve_button(self, obj):
        if obj.status == 'Orçamento':
            return format_html('<a href="{}">Aprovar</a>', reverse('approve_order', args=[obj.pk]))
        return 'Aprovado'
    approve_button.short_description = 'Aprovação'


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)

