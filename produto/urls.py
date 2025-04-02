from django.urls import path
from . import views

app_name = 'produto'

urlpatterns = [
    path('', views.ListaProdutos.as_view(), name='lista'),
    path('produto/<slug>/', views.DetalheProduto.as_view(), name='detalhe'),
    path('addcarrinho/', views.AddCarrinho.as_view(), name='addcarrinho'),
    path('removerdocarrinho/', views.RemoverDoCarrinho.as_view(), name='removerdocarrinho'),
    path('carrinho/', views.Carrinho.as_view(), name='carrinho'),
    path('resumodacompra/', views.ResumoDaCompra.as_view(), name='resumodacompra'),
    path('pesquisar/', views.Pesquisar.as_view(), name='pesquisar'),
]
