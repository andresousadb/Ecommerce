# from django.http import JsonResponse
# from store.models import Product
from django.shortcuts import render, redirect
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
import datetime
from django.contrib import messages
# import json
# from django.template.loader import render_to_string
# from django.core.mail import EmailMessage

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count < 1:
        return redirect('store')

    grand_total = 0
    total = 0
    for item in cart_items:
            if item.product.discount_price:
                total += round(((item.product.discount_price) * item.quantity), 2)
                quantity += item.quantity
            else:
                total += round(((item.product.price) * item.quantity), 2)
                quantity += item.quantity

    tax = round(((2 * total) / 100), 2)
    grand_total = round( total, 2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.f_name = form.cleaned_data['Nome']
            data.l_name = form.cleaned_data['último Nome']
            data.tel = form.cleaned_data['Telefone']
            data.city = form.cleaned_data['Cidade']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            if request.POST.get('terms', None) == None:
                # messages.error(request, 'You must accept terms & conditions! Please go back to cart and restart checkout process.')
                return render(request, 'store/checkout.html')
            else:
                data.save()

            year = int(datetime.date.today().strftime('%Y'))
            month = int(datetime.date.today().strftime('%m'))
            day = int(datetime.date.today().strftime('%d'))
            d = datetime.date(year, month, day)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total
            }


            return render(request, 'orders/payment.html', context)

        else:
            messages.error(request, 'Invalid inputs!')
            return redirect('checkout')
