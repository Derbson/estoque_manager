from django import forms
from django.forms import inlineformset_factory
from produtos.models import Produto
from pedidos.models import Pedido, ItemPedido

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['codigo', 'ean', 'descricao', 'cor', 'tamanho', 'quantidade']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    fields=('produto', 'quantidade'),
    extra=1,
    can_delete=True,
    widgets={
        'produto': forms.Select(attrs={'class': 'select2'}),
    }
)