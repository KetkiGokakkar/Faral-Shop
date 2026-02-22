# shop/tests.py
from django.test import TestCase
from backend.shop.models import Product
from backend.shop.serializers import OrderSerializer

class OrderCreationTests(TestCase):
    def setUp(self):
        self.p1 = Product.objects.create(name='Test Item', price=100, stock=5, is_active=True)
        self.p2 = Product.objects.create(name='Item 2', price=50, stock=2, is_active=True)

    def test_order_reduces_stock(self):
        data = {
            "customer": {"name": "Test", "phone": "9999999999"},
            "address": {"line1": "Addr", "city": "City", "pincode": "000001"},
            "items": [
                {"product_id": self.p1.id, "quantity": 2},
                {"product_id": self.p2.id, "quantity": 1}
            ],
            "payment_method": "COD",
            "notes": "none"
        }
        # prepare serializer with incoming format where product_id maps to product instance
        # To use our serializer which expects 'product' object resolved by PK field, we should use the view or adapt the test:
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        req = factory.post('/api/orders/', data, format='json')
        # call view or serializer directly: serializer resolution will map product_id -> Product instance thanks to PrimaryKeyRelatedField
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        order = serializer.save()
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.assertEqual(self.p1.stock, 3)  # 5 - 2
        self.assertEqual(self.p2.stock, 1)  # 2 - 1
