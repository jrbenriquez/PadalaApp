from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model

from padala.models.generics import TimeStampedModelMixin, SixDigitPINMixin

User = get_user_model()


class CustomerProfile(TimeStampedModelMixin):
    user = models.OneToOneField(User, related_name='customer_profile', on_delete=models.PROTECT)
    last_transfer = models.OneToOneField('padala.Transfer', null=True, related_name='last_transfer_of', on_delete=models.SET_NULL)

    @classmethod
    def create_customer(cls, mobile_number, first_name=None, last_name=None, email=None, *args, **kwargs):
        location = kwargs.get('location')

        user = User.create_user(first_name=first_name, last_name=last_name, mobile_number=mobile_number, email=email,
                                **kwargs)
        customer_profile = cls.objects.create(user=user)

        return customer_profile


class AgentProfile(TimeStampedModelMixin):
    user = models.OneToOneField(User, related_name='agent_profile', on_delete=models.PROTECT)
    location = models.CharField(max_length=128, null=True, blank=True)
    transfer_limit = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal(5000))

    @classmethod
    def create_agent(cls, mobile_number, first_name=None, last_name=None, email=None, *args, **kwargs):

        location = kwargs.get('location')

        user = User.create_user(first_name=first_name, last_name=last_name, mobile_number=mobile_number, email=email, **kwargs)
        agent_profile = cls.objects.create(user=user, location=location)

        return agent_profile


class AuthPIN(SixDigitPINMixin):
    transfer = models.OneToOneField('padala.Transfer', related_name='authorization_pin', on_delete=models.CASCADE)

    def send_pin_to_receiver(self):
        pass

    @classmethod
    def create_pin(cls, transfer):
        pin = cls.objects.create(transfer=transfer)
        pin.set_pin()
        return pin
