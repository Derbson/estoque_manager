from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.urls import reverse
from django.shortcuts import redirect

class CustomLoginView(LoginView):
    template_name = 'autenticacao/login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_redirect_url())
        return super().dispatch(request, *args, **kwargs)
    
    def get_redirect_url(self):
        """Redireciona para a página adequada após login"""
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse('estoque:produto_list')
        elif hasattr(self.request.user, 'loja'):
            return reverse('lojas:produtos_disponiveis')
        # Se não for nenhum dos casos acima, redireciona de volta para o login
        return reverse('autenticacao:login')

class CustomLogoutView(LogoutView):
    next_page = 'autenticacao:login'

class RedirectUserView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        """Redireciona usuários autenticados para a página correta"""
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse('estoque:produto_list')
        elif hasattr(self.request.user, 'loja'):
            return reverse('lojas:produtos_diponiveis')
        # Padrão: redireciona para a página de login novamente
        return reverse('autenticacao:login')