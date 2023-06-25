from django.shortcuts import render
from rest_framework import generics
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemsSerializer, UsersSerializers, CartSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date

class MenuItemsView(generics.ListCreateAPIView):
    queryset= MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    search_fields = ['title','category__title']
    ordering_fields=['price','category']

    def get_permissions(self):
        manager_group = self.request.user.groups.filter(name='Manager').exists()
        permission_classes = [IsAuthenticated , IsAdminUser]
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        if  manager_group and self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
        
            

class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer

    def get_permissions(self):
        manager_group = self.request.user.groups.filter(name='Manager').exists()
        permission_classes = [IsAuthenticated, IsAdminUser]
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        if manager_group and self.request.method != 'POST':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
            
        


class ManagersListView(generics.ListCreateAPIView):
    serializer_class = UsersSerializers

    def get_queryset(self):
        manager_group = Group.objects.get(name='Manager')
        return User.objects.filter(groups=manager_group)
    
    def get_permissions(self):
        manager_group = self.request.user.groups.filter(name='Manager').exists()
        permission_classes = [IsAdminUser]
        if manager_group and (self.request.method in ['POST', 'GET']):
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

 

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'message':f'{user.username} added to (Manager) group'}, status=status.HTTP_201_CREATED)
        


class ManagersRemoveView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups__name= "Manager")
    serializer_class = UsersSerializers

    def get_permissions(self):
        manager_group = self.request.user.groups.filter(name='Manager').exists()
        permission_classes = [IsAdminUser]
        if manager_group and (self.request.method in ['GET','DELETE']):
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]



    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        user = get_object_or_404(User, pk=obj.id)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message': f'{user.username} removed from (Manager) group'}, status=status.HTTP_200_OK)

class DeliveryCrewListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UsersSerializers

    def get_permissions(self):
        manager_group = self.request.user.groups.filter(name='Manager').exists()
        permission_classes = [IsAdminUser]
        if manager_group and (self.request.method in ['POST', 'GET']):
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        user = get_object_or_404(User, username=username)
        delivery_crew = Group.objects.get(name='Delivery crew')
        delivery_crew.user_set.add(user)
        return Response({'message': f'{user.username} added to (Delivery crew) group'})


class DeliveryCrewRemoveView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UsersSerializers

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        user = get_object_or_404(User, pk=obj.id)
        delivery_crew = Group.objects.get(name='Delivery crew')
        delivery_crew.user_set.remove(user)
        return Response({'message': f'{user.username} removed from (Delivery crew) group'})
    
    def get_permissions(self):
        manager_group = self.request.user.groups.filter(name='Manager').exists()
        permission_classes = [IsAdminUser]
        if manager_group and (self.request.method in ['GET','DELETE']):
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query_set = Cart.objects.select_related('menuitem').filter(user=self.request.user)
        return query_set
    

    def perform_create(self, serializer):
        user = self.request.user
        quantity = serializer.validated_data['quantity']
        unit_price = serializer.validated_data['menuitem'].price
        price = quantity * unit_price
        try:
            serialized_data = serializer.save(price=price, user=user, unit_price=unit_price)
        except:
            return Response({'message': 'item is already in the cart'})
        return Response(serializer.data)
        

    def delete(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        cart.delete()
        return Response({'message': 'Deleted'})
    

class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            if self.request.user.groups.filter(name='Manager').exists():
                queryset = Order.objects.all()
            elif self.request.user.groups.filter(name='Delivery crew').exists():
                queryset = Order.objects.filter(delivery_crew=self.request.user)
            else:
                queryset = Order.objects.filter(user=self.request.user)
        return queryset
    
    def get_permissions(self):
        manager_group = self.request.user.groups.filter(name='Manager').exists()
        delivery_crew_group = self.request.user.groups.filter(name='Delivery crew').exists()
        permission_classes = [IsAdminUser]
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        if self.request.method == 'POST' and not manager_group and not delivery_crew_group:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        cart_list = cart.values()
        if len(cart_list):
            total_price = 0
            for cart_item in cart_list:
                total_price = total_price + cart_item['price']
            order = Order.objects.create(status=False, total=total_price, user=request.user)
            for cart_item in cart_list:
                menuitem= get_object_or_404(MenuItem, id=cart_item['menuitem_id'])
                order_item = OrderItem.objects.create(order=order, menuitem=menuitem, price=cart_item['price'], quantity=cart_item['quantity'], unit_price=cart_item['unit_price'])
            cart.delete()
            return Response({'message': f'Your order has been placed! Your order number is {str(order.id)}'},status=status.HTTP_201_CREATED)
        return Response({'message': 'cart is empty'}, status=status.HTTP_200_OK)


class OrderItemsView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = OrderItem.objects.filter(order_id=self.kwargs['pk'])
        return queryset
    
    def get_permissions(self):
        is_Delivery_crew = self.request.user.groups.filter(name='Delivery crew').exists()
        is_Manager = self.request.user.groups.filter(name='Manager').exists()
        is_Customer = not is_Manager and not is_Delivery_crew
        order = get_object_or_404(Order, pk=self.kwargs['pk'])

        permission_classes = [IsAdminUser]
        if self.request.method == 'GET' and is_Customer and self.request.user == order.user:
            permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH' and (is_Delivery_crew or is_Manager): 
            permission_classes = [IsAuthenticated]
        if self.request.method == 'Delete' and is_Manager:
            permission_classes = [IsAuthenticated]
        if self.request.method == 'PUT' and is_Manager:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


            

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['pk'])
        order.delete()
        return Response({'message': f'order {order.id} deleted'}, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = self.request.data['status']
        order.save()
        return Response({'message': f'order status is updated to {order.status}'})
    
    def put(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery_crew_pk= serializer.data['delivery_crew']
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        crew = get_object_or_404(User, pk=delivery_crew_pk)
        order.delivery_crew = crew
        order.status = serializer.data['status']
        order.save()
        order_status = order.status
        delivery_crew_name = User.objects.get(id=delivery_crew_pk).username
        return Response({'message': f'order {order.id} assigned to {delivery_crew_name} and order status is {order_status}'})


        
        
        
    

