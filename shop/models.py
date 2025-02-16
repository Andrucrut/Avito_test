from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image_url = models.CharField(max_length=512)

    def save(self, *args, **kwargs):
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Coin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

    def clean(self):
        if self.balance < 0:
            raise ValidationError("Coin balance cannot be negative")

    def __str__(self):
        return f"Coin balance for {self.user.username}"

    def add_coins(self, amount):
        if amount < 0:
            raise ValidationError("Cannot add negative coins")
        self.balance += amount
        self.save()

    def subtract_coins(self, amount):
        if amount < 0:
            raise ValidationError("Cannot subtract negative coins")
        if self.balance < amount:
            raise ValidationError("Insufficient balance")
        self.balance -= amount
        self.save()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.total_price < 0:
            raise ValidationError("Total price cannot be negative")

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        if self.price < 0:
            raise ValidationError("Price cannot be negative")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('transfer', 'Transfer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative")

    def __str__(self):
        return f"{self.type} - {self.amount} by {self.user.username}"


class CoinTransaction(models.Model):
    sender = models.ForeignKey(User, related_name="sent_transactions", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_transactions", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative")
        if self.sender != self.recipient:
            sender_coin = Coin.objects.get(user=self.sender)
            if sender_coin.balance < self.amount:
                raise ValidationError("Sender does not have enough coins")

    def __str__(self):
        return f"Transaction from {self.sender.username} to {self.recipient.username} of {self.amount} coins"


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.quantity < 0:
            raise ValidationError("Inventory quantity cannot be negative")

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
