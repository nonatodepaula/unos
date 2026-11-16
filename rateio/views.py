from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Evento, Participante
from .forms import EventoForm, ParticipanteForm, EditarParticipanteForm, MinhaParticipacaoForm

@login_required
def lista_eventos(request):
    eventos_abertos = Evento.objects.filter(status='ABERTO').order_by('-criado_em')
    eventos_encerrados = Evento.objects.filter(status='ENCERRADO').order_by('-criado_em')
    return render(request, 'rateio/lista_eventos.html', {
        'eventos_abertos': eventos_abertos,
        'eventos_encerrados': eventos_encerrados
    })

@login_required
def detalhe_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    resumo = evento.resumo_participantes()
    user_participante = evento.participantes.filter(usuario=request.user).first()
    rateio = evento.calcular_rateio()

    form_minha = MinhaParticipacaoForm(instance=user_participante)
    form_participante = ParticipanteForm()

    return render(request, 'rateio/detalhe_evento.html', {
        'evento': evento,
        'resumo': resumo,
        'user_participante': user_participante,
        'rateio': rateio,
        'form_minha': form_minha,
        'form_participante': form_participante,
    })

@login_required
def criar_evento(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.criador = request.user
            evento.save()
            Participante.objects.create(
                evento=evento,
                usuario=request.user,
                modalidade='RANCHO_CAFE'
            )
            messages.success(request, 'Evento de alimentação criado com sucesso!')
            return redirect('detalhe_evento', pk=evento.pk)
    else:
        form = EventoForm()
    return render(request, 'rateio/criar_evento.html', {'form': form})

@login_required
def alternar_status_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if evento.status == 'ABERTO':
        evento.status = 'ENCERRADO'
        messages.success(request, f'O evento "{evento.titulo}" foi encerrado.')
    else:
        evento.status = 'ABERTO'
        messages.info(request, f'O evento "{evento.titulo}" foi reaberto.')
    evento.save()
    return redirect('detalhe_evento', pk=evento.pk)

@login_required
def entrar_ou_atualizar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if evento.status == 'ENCERRADO':
        messages.error(request, 'Não é possível alterar participação em um evento encerrado.')
        return redirect('detalhe_evento', pk=evento.pk)

    if request.method == 'POST':
        participante = evento.participantes.filter(usuario=request.user).first()
        form = MinhaParticipacaoForm(request.POST, instance=participante)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.evento = evento
            obj.usuario = request.user
            if obj.modalidade == 'SO_EXTRA':
                obj.contrib_rancho = 0
                obj.contrib_cafe = 0
            elif obj.modalidade == 'SO_CAFE':
                obj.contrib_rancho = 0
            obj.save()
            messages.success(request, 'Sua modalidade e contribuições foram atualizadas!')
    return redirect('detalhe_evento', pk=evento.pk)

@login_required
def adicionar_participante(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if evento.status == 'ENCERRADO':
        messages.error(request, 'Não é possível adicionar participantes em um evento encerrado.')
        return redirect('detalhe_evento', pk=evento.pk)

    if request.method == 'POST':
        form = ParticipanteForm(request.POST)
        if form.is_valid():
            participante = form.save(commit=False)
            participante.evento = evento
            if Participante.objects.filter(evento=evento, usuario=participante.usuario).exists():
                messages.warning(request, 'Este usuário já participa do evento. Use a edição na tabela ao lado.')
            else:
                if participante.modalidade == 'SO_EXTRA':
                    participante.contrib_rancho = 0
                    participante.contrib_cafe = 0
                elif participante.modalidade == 'SO_CAFE':
                    participante.contrib_rancho = 0
                participante.save()
                messages.success(request, f'Usuário {participante.usuario.username} adicionado ao evento.')
    return redirect('detalhe_evento', pk=evento.pk)

@login_required
def editar_participante(request, evento_pk, part_pk):
    evento = get_object_or_404(Evento, pk=evento_pk)
    if evento.status == 'ENCERRADO':
        messages.error(request, 'Não é possível alterar participantes em um evento encerrado.')
        return redirect('detalhe_evento', pk=evento.pk)

    participante = get_object_or_404(Participante, pk=part_pk, evento=evento)

    if request.method == 'POST':
        form = EditarParticipanteForm(request.POST, instance=participante)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.modalidade == 'SO_EXTRA':
                obj.contrib_rancho = 0
                obj.contrib_cafe = 0
            elif obj.modalidade == 'SO_CAFE':
                obj.contrib_rancho = 0
            obj.save()
            messages.success(request, f'Participante {participante.usuario.username} atualizado com sucesso!')
            return redirect('detalhe_evento', pk=evento.pk)
    else:
        form = EditarParticipanteForm(instance=participante)

    return render(request, 'rateio/editar_participante.html', {
        'evento': evento,
        'participante': participante,
        'form': form
    })

@login_required
def excluir_participante(request, evento_pk, part_pk):
    evento = get_object_or_404(Evento, pk=evento_pk)
    if evento.status == 'ENCERRADO':
        messages.error(request, 'Não é possível remover participantes de um evento encerrado.')
        return redirect('detalhe_evento', pk=evento.pk)

    participante = get_object_or_404(Participante, pk=part_pk, evento=evento)
    if request.method == 'POST':
        nome = participante.usuario.username
        participante.delete()
        messages.success(request, f'Participante {nome} removido do evento.')
        return redirect('detalhe_evento', pk=evento.pk)

    return render(request, 'rateio/excluir_participante.html', {
        'evento': evento,
        'participante': participante
    })

@login_required
def sair_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if evento.status == 'ENCERRADO':
        messages.error(request, 'Não é possível sair de um evento encerrado.')
        return redirect('detalhe_evento', pk=evento.pk)

    Participante.objects.filter(evento=evento, usuario=request.user).delete()
    messages.info(request, 'Você saiu do evento.')
    return redirect('detalhe_evento', pk=evento.pk)

@staff_member_required
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo usuário cadastrado com sucesso!')
            return redirect('lista_eventos')
    else:
        form = UserCreationForm()
    return render(request, 'rateio/cadastrar_usuario.html', {'form': form})
