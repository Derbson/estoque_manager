from django.views.generic import CreateView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Produto
from .forms import ProdutoForm, ImportarProdutosForm
from lojas.models import HistoricoEstoque
import pandas as pd
from django.contrib import messages
from io import BytesIO
from django.http import HttpResponse
from django.db import transaction


class CadastrarProdutoView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/cadastrar_produto.html'
    success_url = reverse_lazy('estoque:produto_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar no histórico de estoque
        HistoricoEstoque.objects.create(
            produto=self.object,
            tipo='cadastro',
            quantidade=self.object.quantidade,
            quantidade_anterior=0,
            quantidade_posterior=self.object.quantidade,
            usuario=self.request.user,
            motivo='Cadastro inicial do produto'
        )
        
        return response



class EditarProdutoView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/editar_produto.html'
    success_url = reverse_lazy('estoque:produto_list')

    def form_valid(self, form):
        # Salva os dados originais antes da alteração
        produto_original = Produto.objects.get(pk=self.object.pk)
        quantidade_original = produto_original.quantidade
        motivo = self.request.POST.get('motivo_alteracao', 'Edição via formulário')

        # Executa a atualização do produto
        response = super().form_valid(form)

        # Verifica se houve alteração na quantidade
        diferenca_quantidade = self.object.quantidade - quantidade_original
        if diferenca_quantidade != 0:
            HistoricoEstoque.objects.create(
                produto=self.object,
                tipo='ajuste',
                quantidade=diferenca_quantidade,  # Corrigido: usando 'quantidade' em vez de 'quantity'
                quantidade_anterior=quantidade_original,
                quantidade_posterior=self.object.quantidade,
                usuario=self.request.user,
                motivo=motivo
            )
            messages.success(self.request, f"Estoque ajustado em {diferenca_quantidade} unidades")

        # Verifica outras alterações importantes
        alteracoes = []
        campos_verificar = [
            ('descricao', 'Descrição'),
            ('preco_sellin', 'Preço Sell-In'),
            ('preco_sellout', 'Preço Sell-Out'),
            ('cor', 'Cor'),
            ('tamanho', 'Tamanho')
        ]
        
        for campo, nome in campos_verificar:
            original = getattr(produto_original, campo)
            novo = getattr(self.object, campo)
            if str(original) != str(novo):
                alteracoes.append(f"{nome}: {original} → {novo}")

        if alteracoes:
            messages.info(self.request, " | ".join(alteracoes))
            # Registra edição geral mesmo sem alteração de estoque
            HistoricoEstoque.objects.create(
                produto=self.object,
                tipo='edicao',
                quantidade=0,
                quantidade_anterior=quantidade_original,
                quantidade_posterior=self.object.quantidade,
                usuario=self.request.user,
                motivo=f"{motivo} | {' | '.join(alteracoes)}"
            )

        return response


class ImportarProdutosView(LoginRequiredMixin, FormView):
    template_name = 'produtos/importar_produtos.html'
    form_class = ImportarProdutosForm
    success_url = reverse_lazy('estoque:produto_list')
    
    def form_valid(self, form):
        arquivo = form.cleaned_data['arquivo']
        acao = form.cleaned_data['acao']
        
        try:
            # Ler o arquivo
            if arquivo.name.endswith('.xlsx'):
                df = pd.read_excel(arquivo)
            else:
                df = pd.read_csv(arquivo)
            
            # Converter para dicionário
            dados = df.to_dict('records')
            total_processados = 0
            erros = []
            
            with transaction.atomic():
                for i, item in enumerate(dados, start=1):
                    try:
                        resultado = self.processar_item(item, acao)
                        if resultado:
                            total_processados += 1
                    except Exception as e:
                        erros.append(f"Linha {i}: {str(e)}")
                        continue
            
            if total_processados > 0:
                messages.success(self.request, f"{total_processados} produtos processados com sucesso!")
            
            if erros:
                messages.warning(self.request, f"{len(erros)} erros encontrados:")
                for erro in erros[:5]:  # Mostra apenas os 5 primeiros erros
                    messages.warning(self.request, erro)
                if len(erros) > 5:
                    messages.warning(self.request, f"... e mais {len(erros)-5} erros")
                
        except Exception as e:
            messages.error(self.request, f"Erro ao processar arquivo: {str(e)}")
        
        return super().form_valid(form)
    
    def processar_item(self, item, acao):
        # Validar campos obrigatórios
        if 'codigo' not in item or not item['codigo']:
            raise ValueError("Código do produto é obrigatório")
        
        if 'descricao' not in item or not item['descricao']:
            raise ValueError("Descrição do produto é obrigatória")
        
        # Verificar se código já existe
        if acao == 'cadastrar' and Produto.objects.filter(codigo=item['codigo']).exists():
            raise ValueError(f"Código {item['codigo']} já cadastrado")
        
        # Verificar se EAN já existe (se fornecido)
        if 'ean' in item and item['ean'] and Produto.objects.filter(ean=item['ean']).exclude(codigo=item['codigo']).exists():
            raise ValueError(f"EAN {item['ean']} já cadastrado para outro produto")
        
        # Converter valores vazios/None para valores padrão
        quantidade = int(item.get('quantidade', 0))
        preco_sellin = float(item.get('preco_sellin', 0))
        preco_sellout = float(item.get('preco_sellout', 0))
        
        if acao == 'cadastrar':
            # Criar novo produto
            produto = Produto.objects.create(
                codigo=item['codigo'],
                ean=item.get('ean', ''),
                descricao=item['descricao'],
                cor=item.get('cor', ''),
                tamanho=item.get('tamanho', ''),
                quantidade=quantidade,
                preco_sellin=preco_sellin,
                preco_sellout=preco_sellout
            )
            
            # Registrar no histórico
            HistoricoEstoque.objects.create(
                produto=produto,
                tipo='importacao',
                quantidade=quantidade,
                quantidade_anterior=0,
                quantidade_posterior=quantidade,
                usuario=self.request.user,
                motivo='Cadastro em massa via planilha'
            )
            
            return True
            
        elif acao == 'atualizar':
            # Atualizar produto existente
            produto = Produto.objects.get(codigo=item['codigo'])
            quantidade_anterior = produto.quantidade
            
            # Atualizar campos
            produto.descricao = item.get('descricao', produto.descricao)
            produto.ean = item.get('ean', produto.ean)
            produto.cor = item.get('cor', produto.cor)
            produto.tamanho = item.get('tamanho', produto.tamanho)
            produto.quantidade = quantidade
            produto.preco_sellin = preco_sellin
            produto.preco_sellout = preco_sellout
            produto.save()
            
            # Registrar no histórico se quantidade mudou
            if quantidade_anterior != produto.quantidade:
                HistoricoEstoque.objects.create(
                    produto=produto,
                    tipo='importacao',
                    quantidade=produto.quantidade - quantidade_anterior,
                    quantidade_anterior=quantidade_anterior,
                    quantidade_posterior=produto.quantidade,
                    usuario=self.request.user,
                    motivo='Atualização em massa via planilha'
                )
            
            return True    


def download_modelo_importacao(request):
    # Criar um DataFrame de exemplo
    dados = {
        'codigo': ['PROD001', 'PROD002'],
        'descricao': ['Produto Exemplo 1', 'Produto Exemplo 2'],
        'ean': ['7891234567890', '7891234567891'],
        'cor': ['Vermelho', 'Azul'],
        'tamanho': ['P', 'M'],
        'quantidade': [10, 20],
        'preco_sellin': [25.90, 35.50],
        'preco_sellout': [49.90, 69.90]
    }
    df = pd.DataFrame(dados)
    
    # Criar um arquivo Excel em memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Produtos', index=False)
    
    # Configurar a resposta
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=modelo_importacao_produtos.xlsx'
    
    return response


