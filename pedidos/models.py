# pedidos/models.py
from django.db import models
from django.core.validators import MinValueValidator
from lojas.models import Loja, EstoqueLoja, HistoricoEstoque
from produtos.models import Produto
from django.utils import timezone

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
    ]
    
    loja = models.ForeignKey(
        Loja,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name='Loja',
        null=True,
    )
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True
    )
    data_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    observacoes = models.TextField(
        'Observações',
        blank=True,
        null=True
    )
    administrador = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Administrador Responsável'
    )
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_criacao']
        permissions = [
            ('aprovar_pedido', 'Pode aprovar ou recusar pedidos'),
        ]
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.loja.nome} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Se o status foi alterado para aprovado/recusado
        if self.pk:
            original = Pedido.objects.get(pk=self.pk)
            if original.status != self.status and self.status in ['aprovado', 'recusado']:
                self.processar_status()
        super().save(*args, **kwargs)
    
    def processar_status(self):
        """Processa a mudança de status do pedido"""
        if self.status == 'aprovado':
            # Move os itens para o estoque da loja
            for item in self.itens.all():
                estoque_loja, created = EstoqueLoja.objects.get_or_create(
                    loja=self.loja,
                    produto=item.produto
                )
                estoque_loja.quantidade += item.quantidade
                estoque_loja.save()
        
        elif self.status == 'recusado':
            # Devolve os itens para o estoque principal
            for item in self.itens.all():
                item.produto.atualizar_estoque(item.quantidade)
                item.produto.save()

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
        validators=[MinValueValidator(1)]
    )
    preco_sellin = models.DecimalField(
        'Preço Sell-In',
        max_digits=10,
        decimal_places=2,
        help_text='Preço de compra para a loja',
        default=0
    )
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Itens de Pedido'
        unique_together = ('pedido', 'produto')
    
    def __str__(self):
        return f"{self.produto.descricao} - {self.quantidade} un."
    
    def save(self, *args, **kwargs):
        # Define o preço sellin automaticamente ao criar
        if not self.pk:
            self.preco_sellin = self.produto.preco_sellin
            # Remove do estoque principal imediatamente
            self.produto.atualizar_estoque(-self.quantidade)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Devolve ao estoque principal se o pedido ainda está pendente
        if self.pedido.status == 'pendente':
            self.produto.atualizar_estoque(self.quantidade)
        super().delete(*args, **kwargs)
    
    @property
    def subtotal(self):
        return self.quantidade * self.preco_sellin
    
    def save(self, *args, **kwargs):
        if self.pk:  # Se já existe (atualização)
            original = ItemPedido.objects.get(pk=self.pk)
            if original.quantidade != self.quantidade:
                self.registrar_historico('ajuste', f"Ajuste de quantidade no pedido #{self.pedido.id}")
        else:  # Novo item
            self.registrar_historico('pedido', f"Pedido #{self.pedido.id}")
        
        super().save(*args, **kwargs)
    
    def registrar_historico(self, tipo, motivo):
        HistoricoEstoque.objects.create(
            produto=self.produto,
            loja=self.pedido.loja,
            tipo=tipo,
            quantidade=self.quantidade,
            quantidade_anterior=self.produto.quantidade,
            quantidade_posterior=self.produto.quantidade - self.quantidade,
            usuario=self.pedido.loja.usuario,
            motivo=motivo,
            pedido=self.pedido
        )


