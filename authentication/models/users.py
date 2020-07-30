from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import PermissionsMixin

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, null=True, unique=True)
    email = models.EmailField(null=True, unique=True, max_length=255)
    first_name = models.CharField(null=True, max_length=255)
    middle_name = models.CharField(null=True, max_length=255)
    last_name = models.CharField(null=True, max_length=255)
    mobile_number = models.CharField(max_length=16, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @classmethod
    def create_user(cls, *args, **kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')
        mobile_number = kwargs.get('mobile_number')
        first_name = kwargs.get('first_name')
        middle_name = kwargs.get('middle_name')
        last_name = kwargs.get('last_name')
        password = kwargs.get('password')

        if not mobile_number:
            raise ValidationError('Mobile Number must be set')

        user = cls.objects.create(
            username=username, email=email,
            mobile_number=mobile_number, first_name=first_name,
            middle_name=middle_name, last_name=last_name)

        if password:
            user.set_password(password)
            user.save(update_fields=['password'])

        return user

    @property
    def is_customer(self):
        if hasattr(self, 'customer_profile'):
            return True
        return False

    @property
    def is_agent(self):
        if hasattr(self, 'agent_profile'):
            return True
        return False




