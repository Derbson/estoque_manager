from django.urls import path
from . import views

app_name = 'lojas'

urlpatterns = [
    path('produtos/', views.ProdutosDisponiveisView.as_view(), name='produtos_disponiveis'),
    path('pedidos/novo/', views.FazerPedidoView.as_view(), name='fazer_pedido'),
    path('pedidos/', views.ListaPedidosView.as_view(), name='lista_pedidos'),
    path('pedidos/<int:pk>/', views.DetalhePedidoView.as_view(), name='detalhe_pedido'),
    path('estoque/', views.EstoqueLojaView.as_view(), name='estoque_loja'),
]