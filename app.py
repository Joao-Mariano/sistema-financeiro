import os

from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from sqlalchemy import URL, text

from extensions import db, login_manager
from models import Usuario, Categoria, Receita, Recorrencia, CompraParcelada, Despesa

from routes.auth import auth_bp

from services.scheduler import iniciar_agendador

load_dotenv()


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

database_url_env = os.environ.get("DATABASE_URL")

if database_url_env:
    if database_url_env.startswith("postgres://"):
        database_url_env = database_url_env.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif database_url_env.startswith("postgresql://"):
        database_url_env = database_url_env.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url_env

else:
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ.get("DB_USER", "postgres"),
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        database=os.environ.get("DB_NAME", "sistema_financeiro")
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
    return redirect(url_for("auth.login"))


def inicializar_aplicacao():

    with app.app_context():
        db.create_all()
        db.session.execute(text("SELECT 1"))

        print("Conexão com PostgreSQL realizada com sucesso!")
        print("Tabelas verificadas/criadas com sucesso!")

        iniciar_agendador(app)


inicializar_aplicacao()


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)