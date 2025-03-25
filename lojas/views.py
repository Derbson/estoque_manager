from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from produtos.models import Produto
from pedidos.models import Pedido, ItemPedido
from .models import Loja, EstoqueLoja
from .forms import FazerPedidoForm, ItemPedidoFormSet
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import LojaRegistrationForm


class ProdutosDisponiveisView(ListView):
    model = Produto
    template_name = 'lojas/produtos_disponiveis.html'
    context_object_name = 'produtos'
    
    def get_queryset(self):
        # Filtra apenas produtos com estoque disponível
        return Produto.objects.filter(quantidade__gt=0).order_by('descricao')

class FazerPedidoView(CreateView):
    model = Pedido
    form_class = FazerPedidoForm
    template_name = 'lojas/fazer_pedido.html'
    success_url = reverse_lazy('lojas:lista_pedidos')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['itens_formset'] = ItemPedidoFormSet(self.request.POST)
        else:
            context['itens_formset'] = ItemPedidoFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        
        # Define a loja automaticamente (simulando a loja logada)
        form.instance.loja = Loja.objects.first()  # Temporário - substituir por loja do usuário
        
        if itens_formset.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            itens_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

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
