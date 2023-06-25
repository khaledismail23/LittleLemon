from django.urls import path
from . import views

urlpatterns = [
  path('menu-items', views.MenuItemsView.as_view()),
  path('menu-items/<int:pk>', views.SingleItemView.as_view()),
  path('groups/managers/users', views.ManagersListView.as_view()),
  path('groups/managers/users/<int:pk>', views.ManagersRemoveView.as_view()),
  path('groups/delivery-crew/users', views.DeliveryCrewListView.as_view()),
  path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewRemoveView.as_view()),
  path('cart/menu-items', views.CartView.as_view()),
  path('orders', views.OrdersView.as_view()),
  path('orders/<int:pk>', views.OrderItemsView.as_view()),
]

