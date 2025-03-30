from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from produtos.models import Produto
from pedidos.models import Pedido, ItemPedido
from .models import Loja, EstoqueLoja
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import LojaRegistrationForm


class ProdutosDisponiveisView(ListView):
    model = Produto
    template_name = 'lojas/produtos_disponiveis.html'
    context_object_name = 'produtos'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(descricao__icontains=search) | queryset.filter(codigo__icontains=search)
        return queryset.order_by('descricao')



class ListaPedidosView(ListView):
    model = Pedido
    template_name = 'lojas/lista_pedidos.html'
    context_object_name = 'pedidos'
    
    def get_queryset(self):
        # Filtra apenas pedidos da loja (simulando a loja logada)
        return Pedido.objects.filter(loja=Loja.objects.first()).order_by('-data_criacao')

class DetalhePedidoView(DetailView):
    model = Pedido
    template_name = 'lojas/detalhe_pedido.html'
    context_object_name = 'pedido'
    
    def get_queryset(self):
        # Filtra apenas pedidos da loja (simulando a loja logada)
        return Pedido.objects.filter(loja=Loja.objects.first())

class EstoqueLojaView(ListView):
    model = EstoqueLoja
    template_name = 'lojas/estoque_loja.html'
    context_object_name = 'estoque'
    
    def get_queryset(self):
        # Filtra apenas estoque da loja (simulando a loja logada)
        return EstoqueLoja.objects.filter(loja=Loja.objects.first()).select_related('produto')


class CadastroLojaView(CreateView):
    form_class = LojaRegistrationForm
    template_name = 'lojas/cadastro_loja.html'
    success_url = reverse_lazy('pagina_inicial')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
