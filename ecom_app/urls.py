from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name="default"),
    path('login', views.user_login, name="login"),
    path('register', views.registration, name="registration"),
    path('logout', views.user_logout, name="logout"),
    path('home', views.home, name="home"),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:cart_item_id>', views.remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:cart_item_id>/<str:action>', views.update_quantity, name='update_quantity'),
    path('update_address/', views.update_address, name='update_address'),
    path('initiate_payment', views.initiate_payment, name='initiate_payment'),
    path('handle_payment_success', views.handle_payment_success, name='handle_payment_success'),
]
