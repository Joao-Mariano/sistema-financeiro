import os

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import URL, text

from extensions import db, login_manager
from models import Usuario, Categoria, Receita, Recorrencia, CompraParcelada, Despesa

from routes.auth import auth_bp

from services.scheduler import iniciar_agendador

load_dotenv()

app = Flask (__name__)

app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]


database_url = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password=os.environ["DB_PASSWORD"],
    host="localhost",
    port=5432,
    database="sistema_financeiro"
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

login_manager.init_app(app)

login_manager.login_view = "auth.login"

app.register_blueprint(auth_bp)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


@app.route("/")
def inicio(): 
    return "Sistema Financeiro - Aplicação em Desenvolvimento e com postgre!!"

if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        db.session.execute(text("SELECT 1"))
        print("Conexão com Postgresql realizada com sucesso!")
        print("Tabelas verificadas/criadas com sucesso")

    iniciar_agendador(app)

    app.run(debug=True, use_reloader=False)