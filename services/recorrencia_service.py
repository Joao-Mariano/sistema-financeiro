from datetime import date, timedelta
from calendar import monthrange

from extensions import db
from models.recorrencia import Recorrencia
from models.despesa import Despesa


def calcular_proximo_vencimento(data_original, periodicidade, ocorrencia=1):

    if periodicidade == "DIARIA":
        return data_original + timedelta(days=ocorrencia)

    elif periodicidade == "SEMANAL":
        return data_original + timedelta(weeks=ocorrencia)

    elif periodicidade == "QUINZENAL":
        return data_original + timedelta(days=15 * ocorrencia)

    intervalos = {
        "MENSAL": 1,
        "BIMESTRAL": 2,
        "TRIMESTRAL": 3,
        "SEMESTRAL": 6,
        "ANUAL": 12
    }

    if periodicidade not in intervalos:
        raise ValueError("Periodicidade inválida.")

    meses_adicionados = intervalos[periodicidade] * ocorrencia

    ano = data_original.year
    mes = data_original.month + meses_adicionados

    ano += (mes - 1) // 12
    mes = ((mes - 1) % 12) + 1

    ultimo_dia = monthrange(ano, mes)[1]

    dia = min(data_original.day, ultimo_dia)

    return date(ano, mes, dia)



def gerar_despesas_recorrentes():

    hoje = date.today()
    limite = hoje + timedelta(days=60)

    recorrencias = Recorrencia.query.filter_by(
        ativa=True
    ).all()

    despesas_geradas = 0

    for recorrencia in recorrencias:

        data_original = recorrencia.data_inicio
        ocorrencia = 0

        while True:

            vencimento = calcular_proximo_vencimento(
                data_original,
                recorrencia.periodicidade,
                ocorrencia
            )

            
            if vencimento < hoje:
                ocorrencia += 1
                continue

            
            if recorrencia.data_fim and vencimento > recorrencia.data_fim:
                break

            
            if vencimento > limite:
                break

            
            despesa_existente = Despesa.query.filter_by(
                id_recorrencia=recorrencia.id_recorrencia,
                data_vencimento=vencimento
            ).first()


            if not despesa_existente:

                nova_despesa = Despesa(
                    id_usuario=recorrencia.id_usuario,
                    id_categoria=recorrencia.id_categoria,
                    id_recorrencia=recorrencia.id_recorrencia,
                    descricao=recorrencia.descricao,
                    valor=recorrencia.valor,
                    data_vencimento=vencimento,
                    status="PENDENTE"
                )

                db.session.add(nova_despesa)
                despesas_geradas += 1

            ocorrencia += 1

        try:
            db.session.commit()

        except Exception as erro:
            db.session.rollback()
            print("Erro ao gerar despesas recorrentes:", erro)
            raise

    return despesas_geradas