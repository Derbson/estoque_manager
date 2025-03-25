from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    # Produtos
    path('produtos/', views.ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', views.ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_update'),
    path('produtos/<int:pk>/', views.ProdutoDetailView.as_view(), name='produto_detail'),
    
    # Pedidos
    path('pedidos/', views.PedidoListView.as_view(), name='pedido_list'),
    path('pedidos/novo/', views.PedidoCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/editar/', views.PedidoUpdateView.as_view(), name='pedido_update'),
    path('pedidos/<int:pk>/', views.PedidoDetailView.as_view(), name='pedido_detail'),
    path('pedidos/<int:pk>/status/<str:status>/', views.atualizar_status_pedido, name='pedido_status'),
]