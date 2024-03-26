import logging
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from .models import Account, Profile
from.forms import RegistrationForm, UserForm, UserProfileForm
from django.utils.html import strip_tags
from cart.models import Cart,CartItem
from cart.views import _cart_id
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from orders.models import Order, OrderProduct
import re



logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Se o formulário é válido, processa os dados
            f_name = form.cleaned_data['f_name']
            l_name = form.cleaned_data['l_name']
            email = form.cleaned_data['email']
            tel = form.cleaned_data['tel']
            password = form.cleaned_data['password']

            # Verifica se a senha atende aos critérios
            if (len(password) < 8 or
                    not any(char.isupper() for char in password) or
                    not any(char.isdigit() for char in password) or
                    not re.search(r'[!@#$%¨&*]', password)):

                messages.error(request, 'A senha precisa atender aos seguintes critérios:\n'
                                        ' * Ao menos 8 caracteres\n'
                                        ' * Ao menos uma letra MAIÚSCULA\n'
                                        ' * Ao menos um número\n'
                                        ' * Ao menos um caractere especial (!@#$%¨&*)')

                return render(request, 'accounts/register.html', {'form': form})
            else:
                pass

            # Verificar se o email já está cadastrado
            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Este email já está cadastrado. Por favor, use outro email.')
                return render(request, 'accounts/register.html', {'form': form})

            # Se o email e o telefone são únicos, cria o usuário
            user = Account.objects.create_user(f_name=f_name, l_name=l_name, email=email, tel=tel, password=password)
            user.save()
            logger.info(f"Usuário criado com sucesso: {user.email}")

            # Envio de e-mail de verificação
            current_site = get_current_site(request)
            subject = 'Ativação de conta'
            body = render_to_string('accounts/register_verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, body, to=[to_email])
            if send_email.send():
                logger.info("E-mail de verificação enviado com sucesso.")
                return redirect('/accounts/login/?command=verification&email=' + email)
            else:
                logger.error("Falha ao enviar o e-mail de verificação.")
                # Se houver falha no envio de e-mail, exibir mensagem de erro genérica
                messages.error(request, 'Ocorreu um erro ao enviar o e-mail de verificação. Por favor, tente novamente.')
                return render(request, 'accounts/register.html', {'form': form})
        else:
            # Se o formulário não é válido, exibe os erros no formulário
            form_errors = "\n".join([strip_tags(error) for error in form.errors])
            logger.error(form_errors)
            return render(request, 'accounts/register.html', {'form': form})
    else:
        # Se a requisição não for POST, exibe o formulário vazio
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})




def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Sua conta está ativada.')
        return redirect('login')
    else:
        messages.error(request, 'Link de ativação inválido! Por favor, tente novamente.')
        return redirect('register')

def login(request):
    if request.method == 'POST': 
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                items_exists = CartItem.objects.filter(cart=cart).exists()
                if items_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciais inválidas!')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, 'Você está desconectado.')
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            subject = 'Solicitação de redefinição de senha.'
            body = render_to_string('accounts/password_reset_request.html', {
                'user':user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, body, to=[to_email])
            send_email.send()
            messages.success(request, 'Se sua conta existir, você receberá um link de redefinição de senha em breve.')
            return redirect('login')
        else:
            messages.error(request, 'Endereço de email invalido!')
            return redirect('forgot_password')
    else:
        return render(request, 'accounts/forgot_password.html')

def validate_reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor redefina sua senha')
        return redirect('reset_password')
    else:
        messages.error(request, 'Link de ativação inválido! Por favor, tente novamente.')
        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Redefinição de senha bem-sucedida.')
            return redirect('login')
        else:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')

@login_required
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id)
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso.')
            return redirect('edit_profile')
        else:
            print("Formulários inválidos!")  # Debugging
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'accounts/edit_profile.html', context)



@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['currentpassword']
        new_password = request.POST['newpassword']
        confirm_password = request.POST['confirmpassword']
        if request.user.is_authenticated:
            user = Account.objects.get(email=request.user.email)
            if new_password == confirm_password:
                # Verifica se a senha atende aos critérios
                if (len(new_password) < 8 or
                        not any(char.isupper() for char in new_password) or
                        not any(char.isdigit() for char in new_password) or
                        not re.search(r'[!@#$%¨&*]', new_password)):
                    messages.error(request, 'A senha precisa atender aos seguintes critérios:\n'
                                            ' * Ao menos 8 caracteres\n'
                                            ' * Ao menos uma letra MAIÚSCULA\n'
                                            ' * Ao menos um número\n'
                                            ' * Ao menos um caractere especial (!@#$%¨&*)')
                    return render(request, 'accounts/change_password.html')
                else:
                    pass

                ok = user.check_password(current_password)
                if ok:
                    user.set_password(confirm_password)
                    user.save()
                    messages.success(request, 'Senha atualizada com sucesso')
                    return redirect('login')
                else:
                    messages.error(request, 'Senha atual errada! Por favor digite novamente.')
            else:
                messages.error(request, 'As senhas não coincidem! Por favor, tente novamente.')
        else:
            # Lidar com o caso em que o usuário não está autenticado
            messages.error(request, 'Usuário não autenticado.')

    return render(request, 'accounts/change_password.html')


@login_required
def my_orders(request, *args, **kwargs):
    message = request.GET.get('message')  # Obtém a mensagem da consulta
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'message': message, 'orders': orders})

@login_required
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    total = order.order_total
    total_formatted = '{:,.2f}'.format(total).replace(',', 'x').replace('.', ',').replace('x', '.')

    # Criar uma lista para armazenar pares de produto e preço formatado
    products_with_price = []

    for prod in order_detail:
        price_pro = prod.product_price
        price_pro_formatted = '{:,.2f}'.format(price_pro).replace(',', 'x').replace('.', ',').replace('x', '.')
        products_with_price.append((prod, price_pro_formatted))

    context = {
        'order_detail': products_with_price,
        'order': order,
        'total_formatado': total_formatted,
    }

    return render(request, 'accounts/order_detail.html', context)




def approve_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.status = 'Aceito'
    order.save()

    # Acessar os itens do pedido associados ao pedido
    order_products = OrderProduct.objects.filter(order=order)

    # Descontar a quantidade de cada produto do estoque
    for order_product in order_products:
        product = order_product.product
        if order.status == 'Aceito':
            product.stock -= order_product.quantity
            product.save()

    return redirect('/admin/orders/order/')


def cancelar_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # Verifica se o status atual do pedido é "Aprovado"
    if order.status == 'Aceito':
        # Acessar os itens do pedido associados ao pedido
        order_products = OrderProduct.objects.filter(order=order)

        for order_product in order_products:
            product = order_product.product
            # Ajusta o estoque do produto
            product.stock += order_product.quantity
            product.save()

    # Altera o status do pedido para "Cancelado"
    order.status = 'Cancelado'
    order.save()

    return redirect('/admin/orders/order/')










