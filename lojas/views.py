from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView
from produtos.models import Produto
from pedidos.models import Pedido
from .models import Loja, EstoqueLoja, HistoricoEstoque
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import LojaRegistrationForm
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin



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



# class AjustarEstoqueView(LoginRequiredMixin, View):
#     def post(self, request, pk):
#         item_estoque = get_object_or_404(EstoqueLoja, pk=pk)
#         tipo_ajuste = request.POST.get('tipo_ajuste')
#         quantidade = int(request.POST.get('quantidade', 0))
#         motivo = request.POST.get('motivo', '')

#         try:
#             if tipo_ajuste == 'entrada':
#                 item_estoque.quantidade += quantidade
#             elif tipo_ajuste == 'saida':
#                 if item_estoque.quantidade >= quantidade:
#                     item_estoque.quantidade -= quantidade
#                 else:
#                     raise ValueError("Quantidade indisponível em estoque")
#             elif tipo_ajuste == 'definir':
#                 item_estoque.quantidade = quantidade
            
#             item_estoque.save()
#             messages.success(request, f'Estoque de {item_estoque.produto.descricao} ajustado com sucesso!')
#         except Exception as e:
#             messages.error(request, f'Erro ao ajustar estoque: {str(e)}')

#         return redirect('lojas:estoque_loja')

class AjustarEstoqueView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item_estoque = get_object_or_404(EstoqueLoja, pk=pk)
        tipo_ajuste = request.POST.get('tipo_ajuste')
        quantidade = int(request.POST.get('quantidade', 0))
        motivo = request.POST.get('motivo', 'Ajuste manual')
        quantidade_anterior = item_estoque.quantidade

        try:
            if tipo_ajuste == 'entrada':
                item_estoque.quantidade += quantidade
            elif tipo_ajuste == 'saida':
                if item_estoque.quantidade >= quantidade:
                    item_estoque.quantidade -= quantidade
                else:
                    raise ValueError("Quantidade indisponível em estoque")
            elif tipo_ajuste == 'definir':
                item_estoque.quantidade = quantidade
            
            item_estoque.save()
            
            # Registrar no histórico
            HistoricoEstoque.objects.create(
                produto=item_estoque.produto,
                loja=item_estoque.loja,
                tipo='ajuste',
                quantidade=quantidade if tipo_ajuste != 'definir' else (quantidade - quantidade_anterior),
                quantidade_anterior=quantidade_anterior,
                quantidade_posterior=item_estoque.quantidade,
                usuario=request.user,
                motivo=motivo
            )
            
            messages.success(request, f'Estoque de {item_estoque.produto.descricao} ajustado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao ajustar estoque: {str(e)}')

        return redirect('lojas:estoque_loja')

class HistoricoEstoqueView(LoginRequiredMixin, ListView):
    model = HistoricoEstoque
    template_name = 'lojas/historico_estoque.html'
    paginate_by = 20
    context_object_name = 'historico'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('produto', 'loja', 'usuario', 'pedido')
        
        # Filtros
        produto_id = self.request.GET.get('produto')
        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)
            
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
            
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if data_inicio and data_fim:
            queryset = queryset.filter(
                data__date__gte=data_inicio,
                data__date__lte=data_fim
            )
        
        return queryset.order_by('-data')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produtos'] = Produto.objects.all()
        context['tipo_choices'] = HistoricoEstoque.TIPO_CHOICES
        return context
