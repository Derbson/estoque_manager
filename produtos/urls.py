from django.urls import path
from .views import CadastrarProdutoView, ImportarProdutosView, download_modelo_importacao, EditarProdutoView


app_name = 'produtos'

urlpatterns = [
    path('cadastrar/', CadastrarProdutoView.as_view(), name='cadastrar'),
    path('importar/', ImportarProdutosView.as_view(), name='importar_produtos'),
    path('importar/modelo/', download_modelo_importacao, name='download_modelo'),
    path('editar/<int:pk>/', EditarProdutoView.as_view(), name='produto_update'),
]



