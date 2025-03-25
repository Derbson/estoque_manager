from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from produtos.models import Produto
from pedidos.models import Pedido, ItemPedido
from .forms import ProdutoForm, PedidoForm, ItemPedidoFormSet

## Views para Produtos ##

class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = 'estoque/produto_list.html'
    context_object_name = 'produtos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(descricao__icontains=search) | queryset.filter(codigo__icontains=search)
        return queryset.order_by('descricao')

class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'estoque/produto_form.html'
    success_url = reverse_lazy('estoque:produto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto cadastrado com sucesso!')
        return super().form_valid(form)

class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'estoque/produto_form.html'
    success_url = reverse_lazy('estoque:produto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return super().form_valid(form)

class ProdutoDetailView(LoginRequiredMixin, DetailView):
    model = Produto
    template_name = 'estoque/produto_detail.html'
    context_object_name = 'produto'

## Views para Pedidos ##

class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'estoque/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-data_criacao')

class PedidoCreateView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'estoque/pedido_form.html'
    success_url = reverse_lazy('estoque:pedido_list')
    
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
        
        if itens_formset.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            itens_formset.save()
            messages.success(self.request, 'Pedido criado com sucesso!')
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class PedidoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'estoque/pedido_form.html'
    
    def get_success_url(self):
        return reverse_lazy('estoque:pedido_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['itens_formset'] = ItemPedidoFormSet(self.request.POST, instance=self.object)
        else:
            context['itens_formset'] = ItemPedidoFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        
        if itens_formset.is_valid():
            response = super().form_valid(form)
            itens_formset.instance = self.object
            itens_formset.save()
            messages.success(self.request, 'Pedido atualizado com sucesso!')
            return response
        else:
            return self.render_to_response(self.get_context_data(form=form))

class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'estoque/pedido_detail.html'
    context_object_name = 'pedido'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = self.object.itens.all().select_related('produto')
        return context

def atualizar_status_pedido(request, pk, status):
    pedido = get_object_or_404(Pedido, pk=pk)
    pedido.status = status
    pedido.save()
    messages.success(request, f'Status do pedido {pedido.numero_pedido} atualizado para {pedido.get_status_display()}')
    return redirect('estoque:pedido_detail', pk=pedido.pk)