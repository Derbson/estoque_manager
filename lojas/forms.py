from django import forms
from django.forms import inlineformset_factory
from pedidos.models import Pedido, ItemPedido
from django.contrib.auth.forms import UserCreationForm
from .models import Loja

class LojaRegistrationForm(UserCreationForm):
    nome = forms.CharField(max_length=100, required=True)
    cnpj = forms.CharField(max_length=18, required=True)
    endereco = forms.CharField(widget=forms.Textarea, required=True)
    telefone = forms.CharField(max_length=20, required=True)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Loja.objects.create(
                usuario=user,
                nome=self.cleaned_data['nome'],
                cnpj=self.cleaned_data['cnpj'],
                endereco=self.cleaned_data['endereco'],
                telefone=self.cleaned_data['telefone']
            )
        return user

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