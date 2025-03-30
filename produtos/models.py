# produtos/models.py
from django.db import models
from django.core.validators import MinValueValidator

class Produto(models.Model):
    # Identificação do produto
    ean = models.CharField(
        'EAN',
        max_length=13,
        unique=True,
        blank=True,
        null=True,
        help_text='Código de barras (opcional)'
    )
    codigo = models.CharField(
        'Código',
        max_length=50,
        unique=True,
        help_text='Código interno do produto'
    )
    
    # Descrição do produto
    descricao = models.CharField(
        'Descrição',
        max_length=200,
        help_text='Nome/descrição do produto'
    )
    
    # Características do produto
    cor = models.CharField(
        'Cor',
        max_length=50,
        blank=True,
        null=True,
        help_text='Cor principal do produto'
    )
    tamanho = models.CharField(
        'Tamanho',
        max_length=10,
        blank=True,
        null=True,
        help_text='Tamanho quando aplicável'
    )
    
    # Controle de estoque e preços
    quantidade = models.PositiveIntegerField(
        'Quantidade em Estoque',
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Quantidade disponível na distribuidora'
    )
    preco_sellin = models.DecimalField(
        'Preço Sell-In',
        max_digits=10,
        decimal_places=2,
        help_text='Preço para revenda (lojas)',
        default=0
    )
    preco_sellout = models.DecimalField(
        'Preço Sell-Out',
        max_digits=10,
        decimal_places=2,
        help_text='Preço para venda final (clientes)',
        default=0
    )
    
    # Datas
    data_cadastro = models.DateTimeField(
        'Data de Cadastro',
        auto_now_add=True
    )
    data_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['descricao']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['ean']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.descricao}"
    
    def atualizar_estoque(self, quantidade):
        """Método para atualizar o estoque de forma segura"""
        if self.quantidade + quantidade < 0:
            raise ValueError("Estoque não pode ficar negativo")
        self.quantidade += quantidade
        self.save()