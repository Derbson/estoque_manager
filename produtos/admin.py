from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de produtos
    list_display = ('codigo', 'ean', 'descricao', 'cor', 'tamanho', 'quantidade', 'data_cadastro')
    
    # Filtros disponíveis
    list_filter = ('cor', 'tamanho')
    
    # Campos de busca
    search_fields = ('codigo', 'ean', 'descricao')
    
    # Campos editáveis diretamente na lista
    list_editable = ('quantidade',)
    
    # Campos exibidos no formulário de edição
    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'ean', 'descricao')
        }),
        ('Características', {
            'fields': ('cor', 'tamanho')
        }),
        ('Estoque', {
            'fields': ('quantidade',)
        }),
        ('Datas', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)  # Seção recolhível
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    
    # Ordenação padrão
    ordering = ('-data_cadastro',)
    
    # Itens por página
    list_per_page = 20
    
    # Mostra o número total de itens no topo
    show_full_result_count = True
    
    # Ativa a busca rápica na sidebar
    search_help_text = 'Pesquise por código, EAN ou descrição'
    
    # Personaliza os labels vazios
    empty_value_display = '-----'
