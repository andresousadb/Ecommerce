from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

from django.utils.translation import gettext_lazy as _

class MyAccountManager(BaseUserManager):
    def create_user(self, f_name, l_name, email, tel=None, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O endereço de e-mail deve ser definido'))
        email = self.normalize_email(email)
        user = self.model(f_name=f_name, l_name=l_name, email=email, tel=tel, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, f_name, l_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superadmin', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError(_('Superusuário deve ter is_admin=True.'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário deve ter is_staff=True.'))
        if extra_fields.get('is_active') is not True:
            raise ValueError(_('Superusuário deve ter is_active=True.'))

        return self.create_user(f_name, l_name, email, None, password, **extra_fields)


class Account(AbstractBaseUser):
    f_name = models.CharField(max_length=50, verbose_name=_('Nome'))
    l_name = models.CharField(max_length=50, verbose_name=_('Sobrenome'))
    email = models.EmailField(max_length=100, unique=True, verbose_name=_('Email'))
    tel = models.CharField(max_length=50, unique=True, blank=True, verbose_name=_('Telefone'))
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['f_name', 'l_name']

    objects = MyAccountManager()

    def fullname(self):
        return f"{self.f_name} {self.l_name}"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


CIDADE = (
    ('Rio Branco', 'Rio Branco'),
    ('Maceió', 'Maceió'),
    ('Macapá', 'Macapá'),
    ('Manaus', 'Manaus'),
    ('Salvador', 'Salvador'),
    ('Fortaleza', 'Fortaleza'),
    ('Brasília', 'Brasília'),
    ('Vitória', 'Vitória'),
    ('Goiânia', 'Goiânia'),
    ('São Luís', 'São Luís'),
    ('Cuiabá', 'Cuiabá'),
    ('Campo Grande', 'Campo Grande'),
    ('Belo Horizonte', 'Belo Horizonte'),
    ('Belém', 'Belém'),
    ('João Pessoa', 'João Pessoa'),
    ('Curitiba', 'Curitiba'),
    ('Recife', 'Recife'),
    ('Teresina', 'Teresina'),
    ('Rio de Janeiro', 'Rio de Janeiro'),
    ('Natal', 'Natal'),
    ('Porto Alegre', 'Porto Alegre'),
    ('Porto Velho', 'Porto Velho'),
    ('Boa Vista', 'Boa Vista'),
    ('Florianópolis', 'Florianópolis'),
    ('São Paulo', 'São Paulo'),
    ('Aracaju', 'Aracaju'),
    ('Palmas', 'Palmas')
)

UF = (
    ('AC', 'AC'),
    ('AL', 'AL'),
    ('AP', 'AP'),
    ('AM', 'AM'),
    ('BA', 'BA'),
    ('CE', 'CE'),
    ('DF', 'DF'),
    ('ES', 'ES'),
    ('GO', 'GO'),
    ('MA', 'MA'),
    ('MT', 'MT'),
    ('MS', 'MS'),
    ('MG', 'MG'),
    ('PA', 'PA'),
    ('PB', 'PB'),
    ('PR', 'PR'),
    ('PE', 'PE'),
    ('PI', 'PI'),
    ('RJ', 'RJ'),
    ('RN', 'RN'),
    ('RS', 'RS'),
    ('RO', 'RO'),
    ('RR', 'RR'),
    ('SC', 'SC'),
    ('SP', 'SP'),
    ('SE', 'SE'),
    ('TO', 'TO')
)


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, verbose_name=_('Usuário'))
    address = models.CharField(max_length=100, blank=True, verbose_name=_('Endereço'))
    city = models.CharField(max_length=100, blank=True, choices=CIDADE, verbose_name=_('Cidade'))
    state = models.CharField(max_length=100, blank=True,choices=UF, verbose_name=_('Estado'))
    country = models.CharField(max_length=100, blank=True,default='Brasil', verbose_name=_('País'))

    def __str__(self):
        return self.user.f_name

    def fulllocation(self):
        return f"{self.city}, {self.state}, {self.country}"



