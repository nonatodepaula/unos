from django.contrib import admin
from .models import Evento, Participante

class ParticipanteInline(admin.TabularInline):
    model = Participante
    extra = 1

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'criador', 'criado_em', 'custo_total')
    list_filter = ('status',)
    inlines = [ParticipanteInline]

@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'evento', 'modalidade', 'contrib_rancho', 'contrib_cafe', 'contrib_extra')
    list_filter = ('modalidade', 'evento')
