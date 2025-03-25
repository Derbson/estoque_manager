from django.contrib import admin

from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
    fields = ('produto', 'quantidade')
    autocomplete_fields = ('produto',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'data_criacao', 'status', 'total_itens')
    list_filter = ('status', 'data_criacao')
    search_fields = ('numero_pedido',)
    readonly_fields = ('numero_pedido', 'data_criacao', 'data_atualizacao')
    inlines = [ItemPedidoInline]
    
    fieldsets = (
        (None, {
            'fields': ('numero_pedido', 'status')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
    
    def total_itens(self, obj):
        return obj.total_itens
    total_itens.short_description = 'Total de Itens'

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade')
    list_filter = ('pedido__status',)
    search_fields = ('pedido__numero_pedido', 'produto__descricao')
    autocomplete_fields = ('produto',)
