from django.shortcuts import get_object_or_404, render, redirect
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import render


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)

    if user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(product=product, user=user)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=user,
            )
    else:
        cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )

    return redirect('cart')


def clear_cart(request):
    user = request.user
    if user.is_authenticated:
        CartItem.objects.filter(user=user).delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        CartItem.objects.filter(cart=cart).delete()

    return redirect('cart')

def remove_cart(request, product_id):
    user = request.user
    if user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(user=user, product=product)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except CartItem.DoesNotExist:
            pass
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except CartItem.DoesNotExist:
            pass

    return redirect('cart')

def remove_cart_item(request, product_id):
    user = request.user
    if user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(user=user, product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass

    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    total_formatted = '0.00'

    try:
        tax = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            if item.product.discount_price:
                # Adicionando ao total com formatação correta
                total += round((item.product.discount_price * item.quantity), 2)
                quantity += item.quantity
            else:
                total += round((item.product.price * item.quantity), 2)
                quantity += item.quantity

        total_formatted = '{:,.2f}'.format(total).replace(',', 'x').replace('.', ',').replace('x', '.')

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total_formatted,
        'quantity': quantity,
        'cart_items': cart_items
    }

    return render(request, 'store/cart.html', context)

