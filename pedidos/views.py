from django.views.generic import ListView, FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Pedido, ItemPedido
from .forms import CriarPedidoForm
from produtos.models import Produto
from django.shortcuts import redirect
from django.contrib import messages
from lojas.models import Loja


class ListaPedidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/lista_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset.order_by('-data_criacao')
        return queryset.filter(loja=self.request.user.loja).order_by('-data_criacao')

class CriarPedidoView(LoginRequiredMixin, FormView):
    template_name = 'pedidos/criar_pedido.html'
    form_class = CriarPedidoForm
    success_url = reverse_lazy('pedidos:lista_pedidos')
    
    def form_valid(self, form):
        pedido = Pedido.objects.create(
            loja=self.request.user.loja,
            observacoes=form.cleaned_data['observacoes']
        )
        
        for produto in form.cleaned_data['produtos']:
            quantidade = int(self.request.POST.get(f'quantidade-{produto.id}', 1))
            if quantidade > 0:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=quantidade,
                    preco_sellin=produto.preco_sellin
                )
                produto.atualizar_estoque(-quantidade)
        
        return super().form_valid(form)

class DetalhePedidoView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Pedido
    template_name = 'pedidos/detalhe_pedido.html'
    context_object_name = 'pedido'
    
    def test_func(self):
        pedido = self.get_object()
        return self.request.user.is_superuser or pedido.loja == self.request.user.loja
    

class ListaPedidosAdminView(UserPassesTestMixin, ListView):
    model = Pedido
    template_name = 'pedidos/lista_pedidos_admin.html'
    paginate_by = 25
    context_object_name = 'pedidos'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('loja', 'administrador')
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        loja_id = self.request.GET.get('loja')
        if loja_id:
            queryset = queryset.filter(loja_id=loja_id)
            
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if data_inicio and data_fim:
            queryset = queryset.filter(
                data_criacao__date__gte=data_inicio,
                data_criacao__date__lte=data_fim
            )
        
        return queryset.order_by('-data_criacao')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas
        context['total_pedidos'] = Pedido.objects.count()
        context['pedidos_pendentes'] = Pedido.objects.filter(status='pendente').count()
        context['pedidos_aprovados'] = Pedido.objects.filter(status='aprovado').count()
        context['pedidos_recusados'] = Pedido.objects.filter(status='recusado').count()
        
        # Opções para filtros
        context['status_choices'] = Pedido.STATUS_CHOICES
        context['lojas'] = Loja.objects.all()  # Agora usando o modelo importado corretamente
        
        return context
    
class DetalhePedidoAdminView(UserPassesTestMixin, DetailView):
    model = Pedido
    template_name = 'pedidos/detalhe_pedido_admin.html'
    context_object_name = 'pedido'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Pedido.STATUS_CHOICES
        return context

from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Pedido

class AlterarStatusView(UserPassesTestMixin, View):
    """
    View para alterar o status de um pedido (apenas para superusuários)
    """
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def post(self, request, pk):
        try:
            pedido = Pedido.objects.get(pk=pk)
            novo_status = request.POST.get('status')
            
            # Verifica se o status é válido
            if novo_status not in dict(Pedido.STATUS_CHOICES):
                messages.error(request, 'Status inválido')
                return redirect('pedidos:detalhe_pedido_admin', pk=pk)
            
            # Atualiza o status e o administrador responsável
            pedido.status = novo_status
            pedido.administrador = request.user
            pedido.save()
            
            # Mensagem de sucesso
            messages.success(
                request, 
                f'Status do pedido #{pk} alterado para {pedido.get_status_display()}'
            )
            
            # Redireciona de volta para a lista de pedidos admin
            return redirect('pedidos:lista_pedidos_admin')
            
        except Pedido.DoesNotExist:
            messages.error(request, 'Pedido não encontrado')
            return redirect('pedidos:lista_pedidos_admin')