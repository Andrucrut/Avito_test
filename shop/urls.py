from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, CoinTransactionViewSet, InventoryViewSet, PurchaseViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('orders', OrderViewSet, basename='order')
router.register('coin-transactions', CoinTransactionViewSet)
router.register('inventory', InventoryViewSet)
router.register('purchases', PurchaseViewSet, basename='purchase')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth-token/', include('djoser.urls.authtoken')),
]
