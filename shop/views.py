# shop/views.py
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-placed_at')
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        phone = self.request.query_params.get('phone')
        if phone:
            qs = qs.filter(customer__phone=phone)
        return qs

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_val = request.data.get('status')
        valid = [c[0] for c in Order.STATUS_CHOICES]
        if status_val and status_val in valid:
            order.status = status_val
            order.save()
            return Response({'status': 'ok', 'new_status': order.status})
        return Response({'error': 'invalid status'}, status=status.HTTP_400_BAD_REQUEST)

