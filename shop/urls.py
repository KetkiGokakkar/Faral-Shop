# shop/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductListView, ProductDetailView, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('', include(router.urls)),
]
