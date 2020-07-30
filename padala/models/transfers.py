from django.db import models
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from padala.models.generics import TimeStampedModelMixin
from django.utils.translation import gettext_lazy as _

from padala.models.users import CustomerProfile, AgentProfile, AuthPIN
User = get_user_model()


class Transfer(TimeStampedModelMixin):
    sender = models.ForeignKey(CustomerProfile, related_name='transfers', on_delete=models.PROTECT)
    receiver = models.ForeignKey(CustomerProfile, related_name='received', on_delete=models.PROTECT)

    sending_agent = models.ForeignKey(AgentProfile, related_name='transfers_sent', on_delete=models.PROTECT)
    receiving_agent = models.ForeignKey(AgentProfile, related_name='transfers_received', on_delete=models.PROTECT, null=True)

    class TransferStatus(models.TextChoices):
        PENDING = 'P', _('Pending')
        RELEASING = 'R', _('For Releasing')
        COMPLETE = 'C', _('Complete')

    status = models.CharField(max_length=4, choices=TransferStatus.choices, default=TransferStatus.PENDING)
    amount = models.DecimalField(max_digits=11, decimal_places=2)

    def set_status(self, status):
        if status not in self.TransferStatus:
            raise ValidationError(f'Invalid Status for Transfer {status}')

        self.status = status
        self.save(update_fields=['status'])

    def set_releasing(self):
        self.set_status(self.TransferStatus.RELEASING)

    def lock_in(self, agent):
        self.receiving_agent = agent
        self.save(update_fields=['receiving_agent'])
        self.set_releasing()

    def cash_out(self):
        if self.status == self.TransferStatus.RELEASING:
            return CashOut.create_cashout(self)
        raise ValidationError('Can only cash out for releasing transfers')

    @classmethod
    def retrieve_transfer(cls, tid, auth_pin):
        retrieved = Transfer.objects.filter(id=tid, authorization_pin__pin=auth_pin, status=cls.TransferStatus.PENDING)
        if retrieved:
            return retrieved.get()
        return None

    @transaction.atomic
    def save(self, *args, **kwargs):
        new = self.pk is None
        super().save()
        if new:
            pin = AuthPIN.create_pin(self)


class CashOut(TimeStampedModelMixin):
    sender = models.ForeignKey(CustomerProfile, related_name='cashouts_sent', on_delete=models.PROTECT)
    receiver = models.ForeignKey(CustomerProfile, related_name='cashouts_received', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    agent = models.ForeignKey(AgentProfile, related_name='cashouts', on_delete=models.PROTECT)
    transfer = models.OneToOneField('padala.Transfer', related_name='cashout', on_delete=models.PROTECT)

    @classmethod
    def create_cashout(cls, transfer):

        cashout = cls.objects.create(
            transfer=transfer,
            sender=transfer.sender,
            receiver=transfer.receiver,
            amount=transfer.amount,
            agent=transfer.receiving_agent,
        )
        return cashout


