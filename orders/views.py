from django.http import JsonResponse
from .models import Order, OrderProduct
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from cart.models import Cart, CartItem
from cart.views import _cart_id
from accounts.models import Profile,Account
from store.models import Product, ProductGallery, ReviewRating
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic import View
from django.http import HttpResponse
from .models import Order
from django.utils.decorators import method_decorator
from django.urls import reverse
from decimal import Decimal


@method_decorator(login_required, name='dispatch')
class place_order(View):
    def post(self, request, *args, **kwargs):
        try:
            grand_total = 0

            # Obter os itens do carrinho
            if self.request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=self.request.user, is_active=True)
            else:
                cart = Cart.objects.get(cart_id=_cart_id(self.request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)

            cart_items_data = []
            for item in cart_items:
                cart_item_data = {
                    'product': item.product,
                    'quantity': item.quantity,
                    'subtotal': item.subtotal,
                }
                cart_items_data.append(cart_item_data)

                # Calcular o total do carrinho
                if item.product.discount_price:
                    grand_total += item.product.discount_price * item.quantity
                else:
                    grand_total += item.product.price * item.quantity

            # Formatando o total do carrinho
            grand_total = round(grand_total, 2)
            grand_total_formatted = '{:,.2f}'.format(grand_total).replace(',', 'x').replace('.', ',').replace('x', '.')

            new_order = Order.objects.create(
                user=self.request.user if self.request.user.is_authenticated else None,
                f_name=request.POST.get('f_name', ''),
                l_name=request.POST.get('l_name', ''),
                email=request.POST.get('email', ''),
                tel=request.POST.get('tel', ''),
                city=request.POST.get('city', ''),
                order_total=grand_total,
                status='Orçamento',
                ip=request.META.get('REMOTE_ADDR'),
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            # Atualize o número do pedido com base no ID do pedido recém-criado
            new_order.order_number = timezone.now().strftime('%Y%m%d') + str(new_order.id)
            new_order.save()


            # Inicialize o grand_total fora do loop
            grand_total = Decimal('0')

            # Itere sobre os itens do carrinho
            for item in cart_items:
                if item.product.discount_price:
                    product_price = item.product.discount_price
                else:
                    product_price = item.product.price

                # Calcule o preço total do item (product_price * quantidade)
                total_price_for_item = product_price * item.quantity

                # Adicione o preço total do item ao grand_total
                grand_total += total_price_for_item

                # Salve os dados na tabela OrderProduct
                order_product = OrderProduct.objects.create(
                    order=new_order,
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    product_price=total_price_for_item,  # Use o preço total do item como product_price
                    ordered=True
                )

                # Atualizar o estoque do produto
                item.product.stock -= item.quantity
                item.product.save()


            # Limpar o carrinho após gerar o pedido
            if self.request.user.is_authenticated:
                CartItem.objects.filter(user=self.request.user, is_active=True).delete()
            else:
                CartItem.objects.filter(cart=cart, is_active=True).delete()

            # Adicionar os dados do usuário e da cidade ao contexto
            if self.request.user.is_authenticated:
                try:
                    user = Account.objects.get(id=self.request.user.id)
                    user_profile = Profile.objects.get(user=user)
                    city = user_profile.city
                except Profile.DoesNotExist:
                    city = None
            else:
                city = None

            context = {
                'cart_items': cart_items_data,
                'grand_total': grand_total_formatted,
                'pdf': new_order,  # Adicionar a instância de Order ao contexto
                'city': city,
                'user': user
            }

            # Adicione uma mensagem de sucesso
            message = "Pedido realizado com sucesso!"

            # Obtenha a URL da view 'my_orders'
            my_orders_url = reverse('my_orders')

            # Redirecione para a URL de 'my_orders' com a mensagem como parâmetro de consulta
            return redirect(f'{my_orders_url}?message={message}')

        except ObjectDoesNotExist:
            return HttpResponse("Erro ao processar o pedido. Por favor, tente novamente.")  # Retorna uma resposta de erro

