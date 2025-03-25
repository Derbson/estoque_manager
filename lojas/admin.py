from django.contrib import admin
from .models import Loja

@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'usuario', 'data_cadastro', 'ativo')
    list_filter = ('ativo', 'data_cadastro')
    search_fields = ('nome', 'cnpj', 'usuario__username')
    raw_id_fields = ('usuario',)
