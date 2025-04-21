# autenticacao/urls.py
from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RedirectUserView

app_name = 'autenticacao'

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('redirecionar/', RedirectUserView.as_view(), name='redirecionar_usuario'),
]