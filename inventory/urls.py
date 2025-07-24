# urls.py content
from django.urls import path
from . import views
from .views import StockMovementCreateView, StockMovementListView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('agregar_categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('agregar_proveedor/', views.agregar_proveedor, name='agregar_proveedor'),
    path('import_csv/', views.import_csv, name='import_csv'),
    path('new_movement/', views.new_movement, name='new_movement'),
    path('movements_chart/', views.movements_chart, name='movements_chart'),
    path('movements/', views.StockMovementListView.as_view(), name='stockmovement_list'),
    path('movements/add/', views.StockMovementCreateView.as_view(), name='stockmovement_add'),
]

