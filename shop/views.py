from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, Order, OrderItem, Transaction, Coin, CoinTransaction, Inventory
from .serializers import ProductSerializer, OrderSerializer, TransactionSerializer, InventorySerializer, \
    CoinTransactionSerializer
from django.contrib.auth.models import User


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        order = self.get_object()
        order.status = 'completed'
        order.save()
        return Response({'status': 'order completed'})


class CoinTransactionViewSet(viewsets.ModelViewSet):
    queryset = CoinTransaction.objects.all()
    serializer_class = CoinTransactionSerializer

    @action(detail=False, methods=['post'])
    def transfer_coins(self, request):
        sender = request.user
        recipient_id = request.data.get("recipient_id")
        amount = request.data.get("amount")

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({'error': 'Recipient not found'}, status=404)

        if amount <= 0:
            return Response({'error': 'Amount must be greater than zero'}, status=400)

        sender_coin = sender.coin
        if sender_coin.balance < amount:
            return Response({'error': 'Insufficient balance'}, status=400)

        with transaction.atomic():
            sender_coin.balance -= amount
            recipient_coin, created = Coin.objects.get_or_create(user=recipient)
            recipient_coin.balance += amount

            sender_coin.save()
            recipient_coin.save()

            CoinTransaction.objects.create(sender=sender, recipient=recipient, amount=amount)

        return Response({'status': 'Coins transferred successfully'})


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def purchase(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        total_price = product.price * quantity

        user_coin = user.coin
        if user_coin.balance < total_price:
            return Response({'error': 'Insufficient coins'}, status=400)

        with transaction.atomic():
            user_coin.balance -= total_price
            user_coin.save()

            order = Order.objects.create(user=user, total_price=total_price, status='completed')
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)

        return Response({'status': 'Purchase successful'})


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        inventory = self.get_object()
        new_quantity = request.data.get('quantity')
        if new_quantity is not None:
            inventory.quantity = new_quantity
            inventory.save()
            return Response({'status': 'inventory updated'})
        return Response({'error': 'Quantity is required'}, status=400)
