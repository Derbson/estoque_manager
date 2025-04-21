# autenticacao/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            login_url = reverse('autenticacao:login')
            
            if request.path == login_url:
                # Redireciona por username (adicione seus usuários específicos)
                if request.user.username in ['admin']:  # Substitua pelos usernames desejados
                    return redirect('lojas:produtos')  # URL para esses usuários
                
                if request.user.is_superuser or request.user.is_staff:
                    return redirect('estoque:produto_list')
                elif hasattr(request.user, 'loja'):
                    return redirect('pedidos:lista_pedidos')
                return redirect('home')