from django.test import TestCase
from faker import Faker

from padala.models import User, CustomerProfile, AgentProfile, Transfer, CashOut, AuthPIN

faker = Faker()
# Create your tests here.


class AgentTestCase(TestCase):

    @staticmethod
    def create_agent(**kwargs):

        location = kwargs.get('location', faker.address())
        password = kwargs.get('password', faker.password())
        mobile_number = kwargs.get('mobile_number', faker.phone_number())
        first_name = kwargs.get('first_name', faker.first_name())
        middle_name = kwargs.get('middle_name', faker.last_name()),
        last_name = kwargs.get('last_name', faker.last_name())
        agent = AgentProfile.create_agent(
            mobile_number=mobile_number,
            location=location,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            password=password

        )
        return agent

    def test_bare_agent_created(self):
        """An Agent should be found inside the database"""
        agent = AgentProfile.create_agent(
            mobile_number='+639988836353',
            location='Unknown Location'
        )
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.user)
        self.assertIsNotNone(agent.transfer_limit)

    def test_full_detailed_agent_created(self):
        """An Agent should be found inside the database"""
        mobile_number = '+639988836353'
        location = 'Unknown Location'
        first_name = 'John'
        last_name = 'Cruz'
        password = '1234567890'
        agent = self.create_agent(
            mobile_number=mobile_number,
            location=location,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        self.assertIsNotNone(agent)
        self.assertEqual(agent.user.first_name, first_name)
        self.assertEqual(agent.user.last_name, last_name)
        self.assertEqual(agent.user.mobile_number, mobile_number)
        self.assertTrue(agent.user.check_password(password))
        self.assertEqual(agent.location, location)
        self.assertTrue(agent.user.is_agent)


class CustomerTestCase(TestCase):

    @staticmethod
    def create_customer(**kwargs):
        mobile_number = kwargs.get('mobile_number', faker.phone_number())
        first_name = kwargs.get('first_name', faker.first_name())
        middle_name = kwargs.get('middle_name', faker.last_name())
        last_name = kwargs.get('last_name', faker.last_name())
        return CustomerProfile.create_customer(
            mobile_number=mobile_number,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
        )

    def test_customer_created(self):
        """Customer Profile is created"""
        mobile_number = '+639988836353'
        first_name = 'John'
        middle_name = 'Castillo'
        last_name = 'Cruz'
        customer = self.create_customer(
            mobile_number=mobile_number,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name
        )

        self.assertIsNotNone(customer)
        self.assertEqual(customer.user.mobile_number, mobile_number)
        self.assertEqual(customer.user.first_name, first_name)
        self.assertEqual(customer.user.middle_name, middle_name)
        self.assertEqual(customer.user.last_name, last_name)


class CreateTransfer(TestCase):

    @staticmethod
    def create_transfer():
        sender = CustomerTestCase.create_customer()
        receiver = CustomerTestCase.create_customer()
        sending_agent = AgentTestCase.create_agent()
        transfer = Transfer.objects.create(
            sender=sender,
            receiver=receiver,
            sending_agent=sending_agent,
            amount=3000
        )
        return transfer

    def setUp(self):

        receiving_agent = AgentTestCase.create_agent()

        transfer = self.create_transfer()
        data = {
            'sending_agent': transfer.sending_agent,
            'sender': transfer.sender,
            'receiver': transfer.receiver,
            'transfer': transfer
        }
        self.data = data

    def test_create_transfer(self):
        # Check the Transfer is created
        data = self.data
        transfer = data.get('transfer')
        sending_agent = data.get('sending_agent')
        receiving_agent = data.get('receiving_agent')
        sender = data.get('sender')

        self.assertTrue(bool(Transfer.objects.all()))
        self.assertTrue(bool(AuthPIN.objects.filter(transfer=transfer)))
        self.assertEqual(Transfer.objects.last(), transfer)
        self.assertEqual(transfer.sending_agent, sending_agent)
        self.assertEqual(transfer.sender, sender)


class RetrieveTransfer(TestCase):
    def setUp(self):

        transfer = CreateTransfer.create_transfer()

        data = {
            'sending_agent': transfer.sending_agent,
            'sender': transfer.sender,
            'receiver': transfer.receiver,
            'transfer': transfer
        }
        self.data = data

    def test_retrieve_transfer(self):
        # Check if Transfer can be retrieved using transfer ID and auth pin
        data = self.data

        transfer = data.get('transfer')
        auth_pin = AuthPIN.objects.get(transfer=transfer)

        self.assertTrue(bool(auth_pin))
        self.assertTrue(bool(transfer))

        retrieved = Transfer.retrieve_transfer(transfer.id, auth_pin.pin)
        self.assertTrue(bool(retrieved))
        self.assertIsNone(retrieved.receiving_agent)
        self.assertEqual(retrieved, transfer)


class LockInTransfer(TestCase):
    def setUp(self):
        receiving_agent = AgentTestCase.create_agent()

        transfer = CreateTransfer.create_transfer()
        transfer.receiving_agent = receiving_agent
        transfer.save(update_fields=['receiving_agent'])
        transfer.lock_in(receiving_agent)
        data = {
            'sending_agent': transfer.sending_agent,
            'receiving_agent': transfer.receiving_agent,
            'sender': transfer.sender,
            'receiver': transfer.receiver,
            'transfer': transfer
        }
        self.data = data

    def test_lock_in_transfer(self):
        # Check that Transfer Status is Releasing
        data = self.data
        transfer = data.get('transfer')
        receiving_agent = data.get('receiving_agent')
        self.assertEqual(transfer.status, Transfer.TransferStatus.RELEASING)
        self.assertEqual(transfer.receiving_agent, receiving_agent)
        # Check that any agent won't be able to retrieve the transfer using the id and PIN since it is already locked in to an agent
        auth_pin = AuthPIN.objects.get(transfer=transfer)

        retrieved = Transfer.retrieve_transfer(transfer.id, auth_pin.pin)
        self.assertFalse(bool(retrieved))


class CashOut(TestCase):
    def setUp(self):
        receiving_agent = AgentTestCase.create_agent()

        transfer = CreateTransfer.create_transfer()
        transfer.receiving_agent = receiving_agent
        transfer.save(update_fields=['receiving_agent'])
        transfer.lock_in(receiving_agent)

        cashout = transfer.cash_out()


        data = {
            'sending_agent': transfer.sending_agent,
            'receiving_agent': transfer.receiving_agent,
            'sender': transfer.sender,
            'receiver': transfer.receiver,
            'transfer': transfer,
            'cashout': cashout
        }
        self.data = data

    def test_create_transfer(self):
        # Check that Transfer Status is Complete
        data = self.data
        transfer = data.get('transfer')
        cashout = data.get('cashout')

        self.assertEqual(transfer.cashout, cashout)




