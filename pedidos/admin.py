# pedidos/admin.py
from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
    min_num = 1
    # readonly_fields = ['preco_sellin', 'subtotal']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'loja', 'data_criacao', 'status', 'total_itens_admin', 'total_quantidade_admin')
    list_filter = ('status', 'data_criacao', 'loja')
    search_fields = ('loja__nome', 'id', 'observacoes')
    inlines = [ItemPedidoInline]
    date_hierarchy = 'data_criacao'
    actions = ['aprovar_pedidos', 'recusar_pedidos']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    # Métodos customizados para o admin
    def total_itens_admin(self, obj):
        return obj.itens.count()
    total_itens_admin.short_description = 'Total Itens'
    
    def total_quantidade_admin(self, obj):
        return sum(item.quantidade for item in obj.itens.all())
    total_quantidade_admin.short_description = 'Total Quantidade'
    
    # Actions personalizadas
    def aprovar_pedidos(self, request, queryset):
        queryset.update(status='aprovado', administrador=request.user)
        self.message_user(request, "Pedidos aprovados com sucesso.")
    aprovar_pedidos.short_description = "Aprovar pedidos selecionados"
    
    def recusar_pedidos(self, request, queryset):
        queryset.update(status='recusado', administrador=request.user)
        self.message_user(request, "Pedidos recusados com sucesso.")
    recusar_pedidos.short_description = "Recusar pedidos selecionados"

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade')
    list_filter = ('pedido__loja', 'pedido__status')
    search_fields = ('produto__descricao', 'produto__codigo', 'pedido__id')
    
    def subtotal(self, obj):
        return obj.subtotal
    