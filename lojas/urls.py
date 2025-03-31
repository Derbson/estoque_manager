from django.urls import path
from . import views
from .views import CadastroLojaView, AjustarEstoqueView, HistoricoEstoqueView

app_name = 'lojas'

urlpatterns = [
    path('produtos/', views.ProdutosDisponiveisView.as_view(), name='produtos_disponiveis'),
    path('estoque/', views.EstoqueLojaView.as_view(), name='estoque_loja'),
    path('cadastro/', CadastroLojaView.as_view(), name='cadastro_loja'),
    path('historico/', HistoricoEstoqueView.as_view(), name='historico_estoque'),
    path('ajustar/<int:pk>/', AjustarEstoqueView.as_view(), name='ajustar_estoque'),
]