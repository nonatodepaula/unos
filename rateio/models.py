from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Evento(models.Model):
    STATUS_CHOICES = (
        ('ABERTO', 'Aberto'),
        ('ENCERRADO', 'Encerrado'),
    )
    titulo = models.CharField(max_length=200, verbose_name="Título do Evento")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABERTO', verbose_name="Status")
    criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_criados')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"

    def total_rancho(self):
        return sum((p.contrib_rancho for p in self.participantes.all()), Decimal('0.00'))

    def total_cafe(self):
        return sum((p.contrib_cafe for p in self.participantes.all()), Decimal('0.00'))

    def total_extra(self):
        return sum((p.contrib_extra for p in self.participantes.all()), Decimal('0.00'))

    def custo_total(self):
        return self.total_rancho() + self.total_cafe() + self.total_extra()

    def qtd_rancho(self):
        return self.participantes.filter(modalidade='RANCHO_CAFE').count()

    def qtd_cafe(self):
        return self.participantes.filter(modalidade__in=['RANCHO_CAFE', 'SO_CAFE']).count()

    def qtd_total_participantes(self):
        return self.participantes.count()

    def media_rancho(self):
        n = self.qtd_rancho()
        return round(self.total_rancho() / Decimal(n), 2) if n > 0 else Decimal('0.00')

    def media_cafe(self):
        n = self.qtd_cafe()
        return round(self.total_cafe() / Decimal(n), 2) if n > 0 else Decimal('0.00')

    def media_extra(self):
        n = self.qtd_total_participantes()
        return round(self.total_extra() / Decimal(n), 2) if n > 0 else Decimal('0.00')

    def resumo_participantes(self):
        participantes = list(self.participantes.all())
        n_total = len(participantes)
        if n_total == 0:
            return []

        n_rancho = sum(1 for p in participantes if p.modalidade == 'RANCHO_CAFE')
        n_cafe = sum(1 for p in participantes if p.modalidade in ('RANCHO_CAFE', 'SO_CAFE'))

        t_rancho = self.total_rancho()
        t_cafe = self.total_cafe()
        t_extra = self.total_extra()

        cota_rancho = (t_rancho / Decimal(n_rancho)) if n_rancho > 0 else Decimal('0.00')
        cota_cafe = (t_cafe / Decimal(n_cafe)) if n_cafe > 0 else Decimal('0.00')
        cota_extra = (t_extra / Decimal(n_total)) if n_total > 0 else Decimal('0.00')

        resumo = []
        for p in participantes:
            deve_rancho = cota_rancho if p.modalidade == 'RANCHO_CAFE' else Decimal('0.00')
            deve_cafe = cota_cafe if p.modalidade in ('RANCHO_CAFE', 'SO_CAFE') else Decimal('0.00')
            deve_extra = cota_extra

            total_deve = deve_rancho + deve_cafe + deve_extra
            total_pagou = p.contrib_total()
            saldo = total_pagou - total_deve

            resumo.append({
                'participante': p,
                'total_pagou': round(total_pagou, 2),
                'total_deve': round(total_deve, 2),
                'saldo': round(saldo, 2),
                'saldo_exato': saldo,
            })
        return resumo

    def calcular_rateio(self):
        resumo = self.resumo_participantes()
        if len(resumo) <= 1:
            return []

        credores = []
        devedores = []

        for item in resumo:
            saldo = item['saldo_exato']
            if saldo > Decimal('0.005'):
                credores.append({'usuario': item['participante'].usuario, 'saldo': saldo})
            elif saldo < Decimal('-0.005'):
                devedores.append({'usuario': item['participante'].usuario, 'saldo': -saldo})

        transacoes = []
        c_idx = 0
        d_idx = 0

        while c_idx < len(credores) and d_idx < len(devedores):
            cred = credores[c_idx]
            dev = devedores[d_idx]

            valor = min(cred['saldo'], dev['saldo'])
            if round(valor, 2) > Decimal('0.00'):
                transacoes.append({
                    'devedor': dev['usuario'],
                    'credor': cred['usuario'],
                    'valor': round(valor, 2)
                })

            cred['saldo'] -= valor
            dev['saldo'] -= valor

            if cred['saldo'] <= Decimal('0.005'):
                c_idx += 1
            if dev['saldo'] <= Decimal('0.005'):
                d_idx += 1

        return transacoes


class Participante(models.Model):
    MODALIDADE_CHOICES = (
        ('RANCHO_CAFE', 'Rancho Principal + Café (+ Cota Extra)'),
        ('SO_CAFE', 'Só Café (+ Cota Extra)'),
        ('SO_EXTRA', 'Só Cota Extra'),
    )

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='participantes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participacoes')
    modalidade = models.CharField(
        max_length=20,
        choices=MODALIDADE_CHOICES,
        default='RANCHO_CAFE',
        verbose_name="Modalidade de Participação"
    )
    contrib_rancho = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Gasto c/ Rancho Principal (R$)"
    )
    contrib_cafe = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Gasto c/ Café (R$)"
    )
    contrib_extra = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Gasto c/ Cota Extra (R$)"
    )

    class Meta:
        unique_together = ('evento', 'usuario')

    def contrib_total(self):
        return self.contrib_rancho + self.contrib_cafe + self.contrib_extra

    def __str__(self):
        return f"{self.usuario.username} - {self.get_modalidade_display()} (Total Pago: R$ {self.contrib_total()})"
