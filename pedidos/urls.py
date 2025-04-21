from django.urls import path
from .views import CriarPedidoView, ListaPedidosView, DetalhePedidoView, ListaPedidosAdminView, DetalhePedidoAdminView, AlterarStatusView

app_name = 'pedidos'

urlpatterns = [
    path('pedidos/', CriarPedidoView.as_view(), name='criar_pedido'),
    path('lista/', ListaPedidosView.as_view(), name='lista_pedidos'),
    path('<int:pk>/', DetalhePedidoView.as_view(), name='detalhe_pedido'),

    path('lista_pedidos_admin/', ListaPedidosAdminView.as_view(), name='lista_pedidos_admin'),
    path('admin/<int:pk>/', DetalhePedidoAdminView.as_view(), name='detalhe_pedido_admin'),
    path('alterar-status/<int:pk>/', AlterarStatusView.as_view(), name='alterar_status'),
]

