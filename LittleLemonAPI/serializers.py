from .models import Cart, Category, MenuItem, Order, OrderItem
from django.contrib.auth.models import Group, User
from rest_framework import serializers
from datetime import datetime


class MenuItemsSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        depth = 1

class UsersSerializers(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class CartSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=6, decimal_places=2 ,read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2 ,read_only=True)
    class Meta:
        model = Cart
        fields = ['id','menuitem','quantity', 'price', 'unit_price']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    date = serializers.DateField(read_only=True)
    class Meta:
        model = Order
        fields = ['id','user', 'status', 'total', 'date', 'delivery_crew']
        # depth = 1
    

class MenuItemOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemOrderSerializer(read_only=True)
    quantity = serializers.IntegerField(read_only = True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only = True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only = True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']