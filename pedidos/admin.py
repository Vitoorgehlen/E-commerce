from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

class PedidoAdmin(admin.ModelAdmin):
    inline = [
        ItemPedidoInline
    ]

admin.site.register(Pedido)
admin.site.register(ItemPedido)
