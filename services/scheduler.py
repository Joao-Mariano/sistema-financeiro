from apscheduler.schedulers.background import BackgroundScheduler

from services.recorrencia_service import gerar_despesas_recorrentes


scheduler = BackgroundScheduler()


def iniciar_agendador(app):

    if scheduler.running:
        return

    def executar_geracao():

        with app.app_context():

            try:
                quantidade = gerar_despesas_recorrentes()

                print(
                    f"Verificação de recorrências concluída. "
                    f"Despesas geradas: {quantidade}"
                )

            except Exception as erro:
                print(f"Erro ao gerar despesas recorrentes: {erro}")

    # Verificação inicial
    executar_geracao()

    # Verificações automáticas a cada 24 horas
    scheduler.add_job(
        func=executar_geracao,
        trigger="interval",
        days=1,
        id="gerar_despesas_recorrentes",
        replace_existing=True
    )

    scheduler.start()

    print("Agendador de despesas recorrentes iniciado.")