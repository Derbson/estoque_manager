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
    
    # def get_queryset(self):
    #     # Filtra apenas produtos com estoque disponível
    #     return Produto.objects.filter(quantidade__gt=0).order_by('descricao')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(descricao__icontains=search) | queryset.filter(codigo__icontains=search)
        return queryset.order_by('descricao')

class FazerPedidoView(CreateView):
    model = Pedido
    form_class = FazerPedidoForm
    template_name = 'lojas/fazer_pedido.html'
    success_url = reverse_lazy('lojas:lista_pedidos')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            # Adiciona produtos selecionados via GET (quando vem da página de produtos)
            selected_products = self.request.GET.getlist('produtos')
            if selected_products:
                initial_forms = []
                for prod_id in selected_products:
                    try:
                        produto = Produto.objects.get(id=prod_id)
                        initial_forms.append({
                            'produto': produto,
                            'quantidade': 1
                        })
                    except Produto.DoesNotExist:
                        continue
                context['itens_formset'] = ItemPedidoFormSet(initial=initial_forms)
            else:
                context['itens_formset'] = ItemPedidoFormSet()
        elif self.request.POST:
            context['itens_formset'] = ItemPedidoFormSet(self.request.POST)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        form.instance.loja = self.request.user.loja
        
        if itens_formset.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            # Filtra apenas os itens que foram marcados (com quantidade > 0)
            itens = [item for item in itens_formset.save(commit=False) 
                    if item.quantidade > 0 and item.produto is not None]
            
            for item in itens:
                item.pedido = self.object
                item.save()
            
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
