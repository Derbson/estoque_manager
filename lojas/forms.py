from django import forms
from django.forms import inlineformset_factory
from pedidos.models import Pedido, ItemPedido

class FazerPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Observações sobre o pedido...'
            }),
        }

ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    fields=('produto', 'quantidade'),
    extra=1,
    can_delete=False,
    widgets={
        'produto': forms.Select(attrs={'class': 'form-select'}),
        'quantidade': forms.NumberInput(attrs={'min': 1}),
    }
)