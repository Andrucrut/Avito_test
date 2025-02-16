from django.test import TestCase
from .models import Product, User

class ProductTestCase(TestCase):

    def setUp(self):
        User.objects.create(username="testuser", password="password123")
        Product.objects.create(name="T-shirt", price=20.00, stock=100)

    def test_product_creation(self):
        product = Product.objects.get(name="T-shirt")
        self.assertEqual(product.price, 20.00)
        self.assertEqual(product.stock, 100)

    def test_product_str(self):
        product = Product.objects.get(name="T-shirt")
        self.assertEqual(str(product), "T-shirt")

    def test_product_name(self):
        product = Product.objects.get(name="T-shirt")
        self.assertEqual(product.name, "T-shirt")

    def test_negative_stock(self):
        product = Product.objects.create(name="Hoodie", price=30.00, stock=-5)
        self.assertEqual(product.stock, -5)

    def test_product_price_validation(self):
        with self.assertRaises(ValueError):
            Product.objects.create(name="Jacket", price=-10.00, stock=50)

    def test_multiple_products_creation(self):
        Product.objects.create(name="Sweater", price=25.00, stock=150)
        Product.objects.create(name="Pants", price=40.00, stock=200)
        self.assertEqual(Product.objects.count(), 3)

    def test_product_deletion(self):
        product = Product.objects.get(name="T-shirt")
        product.delete()
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(name="T-shirt")
