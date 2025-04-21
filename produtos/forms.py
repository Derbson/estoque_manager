# produtos/forms.py
from django import forms
from .models import Produto
from django import forms
from django.core.validators import FileExtensionValidator

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'codigo',
            'ean',
            'descricao',
            'cor',
            'tamanho',
            'quantidade',
            'preco_sellin',
            'preco_sellout'
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={'placeholder': 'Nome completo do produto'}),
            'quantidade': forms.NumberInput(attrs={'min': 0}),
            'preco_sellin': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'preco_sellout': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data['quantidade']
        if quantidade < 0:
            raise forms.ValidationError("A quantidade não pode ser negativa")
        return quantidade
    


class ImportarProdutosForm(forms.Form):
    arquivo = forms.FileField(
        label='Planilha de Produtos',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'csv'])],
        help_text="Envie um arquivo XLSX ou CSV com os produtos"
    )
    acao = forms.ChoiceField(
        label='Ação',
        choices=[
            ('cadastrar', 'Cadastrar novos produtos'),
            ('atualizar', 'Atualizar estoque e preços'),
        ],
        widget=forms.RadioSelect
    )