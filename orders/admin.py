from .models import  Order, OrderProduct
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html



class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product_price', 'quantity', 'ordered')
    extra = 0
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'tel', 'email', 'order_total', 'created_at', 'status', 'approve_button','cancelar_button')

    def approve_button(self, obj):
        if obj.status == 'Orçamento' or obj.status == "Cancelado":
            return format_html('<a href="{}">Aprovar</a>', reverse('approve_order', args=[obj.pk]))
    approve_button.short_description = 'Aprovar'

    def cancelar_button(self, obj):
        if obj.status in ['Orçamento', 'Aceito']:
            return format_html('<a href="{}">Cancelar</a>', reverse('cancelar_order', args=[obj.pk]))
        return ''
    cancelar_button.short_description = 'Cancelar'
    cancelar_button.allow_tags = True  # Permitir tags HTML no retorno




admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)

