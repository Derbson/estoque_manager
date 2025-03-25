from django.db import models
from produtos.models import Produto

class Loja(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20)
    
    
    class Meta:
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
    
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