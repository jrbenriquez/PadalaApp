from random import randrange
from django.db import models


class TimeStampedModelMixin(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SixDigitPINMixin(TimeStampedModelMixin):

    pin = models.CharField(max_length=6)

    class Meta:
        abstract = True

    @classmethod
    def generate_pin(cls):
        pin_array = [str(randrange(10)) for _ in range(0, 6)]
        return ''.join(pin_array)

    def set_pin(self):
        self.pin = self.generate_pin()
        self.save(update_fields=['pin'])

