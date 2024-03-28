from django.urls import path
from . import views
from .views import place_order

app_name = 'orders'

urlpatterns = [
    path('OrderProduct/', views.OrderProduct, name='order_produto'),
    # path('order_completed/', views.order_completed, name='order_completed'),
    path('gerar_orcamento/', place_order.as_view(), name='gerar_orcamento'),
]



