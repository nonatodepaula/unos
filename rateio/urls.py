from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.lista_eventos, name='lista_eventos'),
    path('evento/<int:pk>/', views.detalhe_evento, name='detalhe_evento'),
    path('evento/novo/', views.criar_evento, name='criar_evento'),
    path('evento/<int:pk>/status/', views.alternar_status_evento, name='alternar_status_evento'),
    path('evento/<int:pk>/entrar/', views.entrar_ou_atualizar_evento, name='entrar_ou_atualizar_evento'),
    path('evento/<int:pk>/adicionar/', views.adicionar_participante, name='adicionar_participante'),
    path('evento/<int:evento_pk>/participante/<int:part_pk>/editar/', views.editar_participante, name='editar_participante'),
    path('evento/<int:evento_pk>/participante/<int:part_pk>/excluir/', views.excluir_participante, name='excluir_participante'),
    path('evento/<int:pk>/sair/', views.sair_evento, name='sair_evento'),
    path('cadastrar-usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('login/', auth_views.LoginView.as_view(template_name='rateio/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
