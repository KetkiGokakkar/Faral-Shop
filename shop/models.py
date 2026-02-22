# shop/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True)  # e.g., 250g
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.IntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.unit})"

class Customer(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.name or 'Customer'} - {self.phone}"

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.line1}, {self.city} - {self.pincode}"

class Order(models.Model):
    STATUS_NEW = 'NEW'
    STATUS_PREPARING = 'PREPARING'
    STATUS_READY = 'READY'
    STATUS_OUT = 'OUT_FOR_DELIVERY'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_READY, 'Ready'),
        (STATUS_OUT, 'Out for delivery'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, default='COD')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_NEW, db_index=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['placed_at']),
        ]
        ordering = ['-placed_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted product'}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=50, blank=True)
    provider_payment_id = models.CharField(max_length=150, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} for Order {self.order.id}"
