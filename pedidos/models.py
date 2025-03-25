from django.db import models


from django.db import models
from produtos.models import Produto
from django.core.validators import MinValueValidator

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('enviado', 'Enviado para aprovação'),
        ('aprovado', 'Aprovado'),
        ('separacao', 'Em separação'),
        ('despachado', 'Despachado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Identificação básica
    numero_pedido = models.CharField(
        'Número do Pedido',
        max_length=20,
        unique=True,
        blank=True,
        help_text='Número único identificador do pedido'
    )
    
    # Datas importantes
    data_criacao = models.DateTimeField('Data de criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última atualização', auto_now=True)
    
    # Status e acompanhamento
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='rascunho'
    )
    
    # Observações adicionais
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Pedido {self.numero_pedido}" if self.numero_pedido else f"Pedido #{self.id}"
    
    def save(self, *args, **kwargs):
        # Gera número do pedido automaticamente no primeiro save
        if not self.numero_pedido:
            from datetime import datetime
            prefixo = datetime.now().strftime('%Y%m%d')
            self.numero_pedido = f"PD{prefixo}-{self.id or 0}"
        super().save(*args, **kwargs)
    
    @property
    def total_itens(self):
        """Retorna o total de itens no pedido"""
        return sum(item.quantidade for item in self.itens.all())

class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Pedido'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_pedido',
        verbose_name='Produto'
    )
    quantidade = models.PositiveIntegerField(
        'Quantidade',
        validators=[MinValueValidator(1)],
        default=1
    )
    
    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens do pedido'
        unique_together = ('pedido', 'produto')  # Evita duplicação
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.descricao} (Pedido: {self.pedido})"