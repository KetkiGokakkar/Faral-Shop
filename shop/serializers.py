# shop/serializers.py
from rest_framework import serializers
from django.db import transaction
from django.db.models import F
from .models import Category, Product, Customer, Address, Order, OrderItem, Payment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'unit', 'image', 'stock', 'is_active', 'category', 'category_id']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'email']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'customer', 'line1', 'city', 'pincode', 'instructions']

class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True), source='product', write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_detail', 'quantity', 'unit_price']
        read_only_fields = ['unit_price', 'product_detail']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerSerializer()
    address = AddressSerializer(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'address', 'items', 'total_amount', 'payment_method', 'status', 'placed_at', 'scheduled_for', 'notes']
        read_only_fields = ['status', 'placed_at', 'total_amount']

    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer_data = validated_data.pop('customer')
        address_data = validated_data.pop('address', None)

        # Use transaction to ensure atomicity
        with transaction.atomic():
            customer, _ = Customer.objects.get_or_create(
                phone=customer_data.get('phone'),
                defaults={'name': customer_data.get('name'), 'email': customer_data.get('email')}
            )

            address = None
            if address_data:
                # create or attach address
                address = Address.objects.create(customer=customer, **address_data)

            # create order with total 0 for now; items added below
            order = Order.objects.create(customer=customer, address=address, total_amount=0, **validated_data)

            total = 0
            # For each item, attempt to decrement stock atomically
            for item in items_data:
                product = item['product']  # already resolved PK -> Product instance
                qty = item.get('quantity', 1)
                if qty <= 0:
                    raise serializers.ValidationError("Quantity must be at least 1.")

                # Attempt to atomically decrement stock if enough stock exists
                updated = Product.objects.filter(pk=product.id, stock__gte=qty).update(stock=F('stock') - qty)
                if updated == 0:
                    # raise ValidationError to rollback transaction
                    raise serializers.ValidationError(f"Product '{product.name}' is out of stock or insufficient quantity.")

                unit_price = product.price
                OrderItem.objects.create(order=order, product=product, quantity=qty, unit_price=unit_price)
                total += (unit_price * qty)

            # set total and save
            order.total_amount = total
            order.save()
            return order

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'provider', 'provider_payment_id', 'amount', 'status', 'created_at']
