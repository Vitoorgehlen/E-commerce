from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from produto.models import Variacao
from utils import utils
from .models import Pedido, ItemPedido

class DispatchLoginRequiredMixin(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs) # type: ignore
        qs = qs.filter(usuario=self.request.user)
        return qs

class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'
    
class SalvarPedido(View):
    template_name = 'pedido/pagar.html'
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login.'
            )
            return redirect('perfil:criar')
        
        carrinho = self.request.session.get('carrinho')

        if not carrinho:
            messages.error(
                self.request,
                'Seu carrinho está vazio.'
            )
            return redirect('produto:lista')
        
        carrinho_variacao_ids = [ v for v in carrinho]
        bd_variacoes = list(Variacao.objects.select_related('produto')
            .filter(id__in=carrinho_variacao_ids))
        
        for variacao in bd_variacoes:
            if not bd_variacoes:
                messages.error(
                    self.request, 
                    'O carrinho contém itens inválidos.')
                return redirect('produto:lista')
            
            vid = str(variacao.id) # type: ignore

            error_msg_estoque = ''

            estoque = variacao.estoque
            qtd_carrinho = carrinho[vid]['quantidade']
            preco_unt = carrinho[vid]['preco_unitario']
            preco_unt_promo = carrinho[vid]['preco_unitario_promocional']
        
            if estoque < qtd_carrinho:
                carrinho[vid]['quantidade'] = estoque
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt
                carrinho[vid]['preco_quantitativo'] = estoque * preco_unt_promo
                
                error_msg_estoque = 'Estoque insuficiente para alguns produtos do seu carrinho. '\
                'Reduzimos a quantidade desses produtos. Por favor, verifique seu carrinho e as '\
                'novas quantidades atuais.'

                if error_msg_estoque:
                    messages.error(
                        self.request,
                        error_msg_estoque
                    )
                
                self.request.session.save()
                return redirect('produto:carrinho')
            
        qtd_total_carrinho = utils.cart_total_qtd(carrinho)
        valor_total_carrinho = utils.cart_totals(carrinho)
        
        pedido = Pedido(
            usuario=self.request.user,
            total=valor_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C',
        )

        pedido.save()
        
        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promocional=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                ) for v in carrinho.values()
                ]
        )

        del self.request.session['carrinho']

        return redirect(
            reverse(
                'pedidos:pagar',
                kwargs={
                    'pk': pedido.pk
                }
            )
        )

class Detalhe(DispatchLoginRequiredMixin, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/detalhe.html'
    pk_url_kwarg = 'pk'
    
class Lista(DispatchLoginRequiredMixin, ListView):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedido/lista.html'
    paginate_by = 10
    ordering = ['-id']