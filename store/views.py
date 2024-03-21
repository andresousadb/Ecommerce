from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from category.models import Category
from cart.models import Cart, CartItem
from cart.views import _cart_id
from django.shortcuts import render
from accounts.models import Profile,Account
from .forms import ReviewForm
from .models import Product, ProductGallery, ReviewRating
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from easy_pdf.views import PDFTemplateView


def store(request, category_slug=None):
    categories = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        topSelling_products = Product.objects.filter(is_available=True, is_topSelling=True).order_by()[:3]
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        topSelling_products = Product.objects.filter(is_available=True, is_topSelling=True).order_by()[:3]
        product_count = products.count()
    return render(request, 'store/store.html', {'products': paged_products, 'product_count': product_count,
                                                'topSelling_products': topSelling_products})





def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    try:
        orderproduct = CartItem.objects.filter(user=request.user.id, product_id=single_product.id).exists()
    except CartItem.DoesNotExist:
        orderproduct = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    reviews_count = reviews.count()
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'product_gallery': product_gallery,
    }

    return render(request, 'store/product.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_at').filter(
                Q(description__icontains=keyword) | Q(name__icontains=keyword))
        else:
            products = None
    return render(request, 'store/store.html', {'products': products})


@login_required
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        shipping_price = 20  # Preço de envio definido como $20 como exemplo, deve ser desenvolvido para calcular km ou milhas
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

            # Obtendo o perfil do usuário atual
            try:
                user = Account.objects.get(id=request.user.id)
                user_profile = Profile.objects.get(user=request.user)
                city = user_profile.city
            except Profile.DoesNotExist:
                city = None

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            city = None  # Se o usuário não estiver autenticado, não há perfil para obter a cidade

        for item in cart_items:
            total += round((item.product.price * item.quantity), 2)
            quantity += item.quantity

        # Removendo taxas e custo de envio por enquanto
        # tax = round(((2 * total) / 100), 2)  # Taxa definida como 2% como exemplo
        # grand_total = round((total + tax + shipping_price), 2)
        grand_total = round(total, 2)
        # Arredondando o total para 2 casas decimais
        grand_total = round(total, 2)

        # Formatando o total para exibir com separadores de milhares e duas casas decimais
        grand_total_formatted = '{:,.2f}'.format(grand_total).replace(',', 'x').replace('.', ',').replace('x', '.')

    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "city": city,  # Adicionando a cidade ao contexto
        # "tax": tax,
        "grand_total": grand_total_formatted,
        "user_chek" : user,
        # "shipping_price": shipping_price,
    }

    return render(request, 'store/checkout.html', context)



def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            # updated_at
            form.save()
            messages.success(request, 'Review updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                # created_at
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Review created.')
                return redirect(url)


class PedidoPDFView(PDFTemplateView):
    template_name = 'store/pedido_pdf.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

            # Adicionar os dados do carrinho ao contexto
            context['cart_items'] = cart_items_data
            context['grand_total'] = grand_total_formatted

            # Adicionar os dados do perfil do usuário ao contexto
            if self.request.user.is_authenticated:
                try:
                    user = Account.objects.get(id=self.request.user.id)
                    user_profile = Profile.objects.get(user=user)
                    city = user_profile.city
                except Profile.DoesNotExist:
                    city = None
            else:
                city = None

            context['city'] = city
            context['pdf'] = user

        except ObjectDoesNotExist:
            pass

        return context


