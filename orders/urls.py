from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    path('scan/', views.barcode_scan, name='barcode_scan'),
]
