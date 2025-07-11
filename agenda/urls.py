from django.urls import path
from agenda.views import listar_eventos

urlpatterns = [
    path('', listar_eventos, name='listar_eventos'),  # Página inicial
]
