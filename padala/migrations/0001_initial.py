# Generated by Django 3.0.7 on 2020-07-30 08:11

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(blank=True, max_length=128, null=True)),
                ('transfer_limit', models.DecimalField(decimal_places=2, default=Decimal('5000'), max_digits=11)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='agent_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('R', 'For Releasing'), ('C', 'Complete')], default='P', max_length=4)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='received', to='padala.CustomerProfile')),
                ('receiving_agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transfers_received', to='padala.AgentProfile')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers', to='padala.CustomerProfile')),
                ('sending_agent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers_sent', to='padala.AgentProfile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='last_transfer',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_transfer_of', to='padala.Transfer'),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='customer_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CashOut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='agent_cashouts', to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cashouts_received', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cashouts_sent', to=settings.AUTH_USER_MODEL)),
                ('transfer', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='cashout', to='padala.Transfer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPIN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('pin', models.CharField(max_length=6)),
                ('transfer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='authorization_pin', to='padala.Transfer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
