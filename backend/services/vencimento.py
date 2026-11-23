"""
Serviço de cálculo de datas de vencimento.
Ajusta datas para dias úteis (evita sábado e domingo).
"""
import calendar
from datetime import date, timedelta


def calcular_vencimento(ano: int, mes: int, dia: int) -> date:
    """
    Calcula a data de vencimento ajustada.
    
    Regras:
    - Se cair em sábado → move para segunda (dia + 2)
    - Se cair em domingo → move para segunda (dia + 1)
    - Se o dia não existir no mês → usa o último dia do mês
    """
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    dia_ajustado = min(dia, ultimo_dia)
    
    d = date(ano, mes, dia_ajustado)
    
    if d.weekday() == 5:  # Sábado
        d += timedelta(days=2)
    elif d.weekday() == 6:  # Domingo
        d += timedelta(days=1)
    
    return d


def gerar_vencimentos_anuais(ano: int, dia: int) -> list[dict]:
    """
    Gera 12 datas de vencimento para um ano inteiro.
    
    Returns:
        Lista de dicts com {mes, data_vencimento, dia_original, ajustado}
    """
    vencimentos = []
    for mes in range(1, 13):
        data = calcular_vencimento(ano, mes, dia)
        vencimentos.append({
            "mes": mes,
            "data_vencimento": data,
            "dia_original": dia,
            "ajustado": data.day != dia,
        })
    return vencimentos


def verificar_status_vencimento(data_vencimento: date) -> dict:
    """
    Verifica o status de um vencimento em relação à data atual.
    
    Returns:
        Dict com {status, dias_restantes, urgencia}
    """
    hoje = date.today()
    delta = (data_vencimento - hoje).days
    
    if delta < 0:
        return {"status": "VENCIDO", "dias_restantes": delta, "urgencia": "critica"}
    elif delta == 0:
        return {"status": "VENCE_HOJE", "dias_restantes": 0, "urgencia": "alta"}
    elif delta <= 3:
        return {"status": "VENCE_BREVE", "dias_restantes": delta, "urgencia": "media"}
    elif delta <= 7:
        return {"status": "VENCE_SEMANA", "dias_restantes": delta, "urgencia": "baixa"}
    else:
        return {"status": "NO_PRAZO", "dias_restantes": delta, "urgencia": "normal"}


NOMES_MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

NOMES_MESES_ABREV = {
    1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR",
    5: "MAI", 6: "JUN", 7: "JUL", 8: "AGO",
    9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"
}
