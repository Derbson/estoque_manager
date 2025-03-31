# pedidos/forms.py
from django import forms
from produtos.models import Produto
from .models import Pedido

class CriarPedidoForm(forms.Form):
    observacoes = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Observações sobre o pedido...',
            'class': 'form-control'
        }),
        required=False
    )
    
    produtos = forms.ModelMultipleChoiceField(
        queryset=Produto.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produtos'].queryset = Produto.objects.filter(quantidade__gt=0)
