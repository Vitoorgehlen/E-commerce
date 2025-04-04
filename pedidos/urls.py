from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('pagar/<int:pk>', views.Pagar.as_view(), name='pagar'),
    path('lista/', views.Lista.as_view(), name='lista'),
    path('salvarpedido/', views.SalvarPedido.as_view(), name='salvarpedido'),
    path('detalhe/<int:pk>', views.Detalhe.as_view(), name='detalhe'),
]
