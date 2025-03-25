from django.db import models
from django.utils import timezone
from produtos.models import Produto
from django.contrib.auth.models import User

class Loja(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='loja',
        verbose_name='Usuário',
        null=True,  # Temporariamente permitir nulo
        blank=True  # Temporariamente permitir em branco
    )
    nome = models.CharField(
        'Nome da Loja',
        max_length=100,
        unique=True
    )
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        unique=True,
        null=True,  # Temporariamente permitir null
        blank=True  # Temporariamente permitir em branco
    )
    endereco = models.TextField(
        'Endereço Completo'
    )
    telefone = models.CharField(
        'Telefone',
        max_length=20
    )
    data_cadastro = models.DateTimeField(
        'Data de Cadastro',
        null=True,  # Temporariamente permitir null
        blank=True,  # Temporariamente permitir em branco
        # auto_now_add=True,

    )
    ativo = models.BooleanField(
        'Ativa?',
        default=True
    )

    class Meta:
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class EstoqueLoja(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name='estoque')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('loja', 'produto')
        verbose_name = 'Estoque da Loja'
        verbose_name_plural = 'Estoques das Lojas'
    
    def __str__(self):
        return f"{self.loja.nome} - {self.produto.descricao}: {self.quantidade}"