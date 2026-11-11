import os

from flask import Flask
from sqlalchemy import URL, text

from extensions import db
from models import Usuario, Categoria, Receita, Recorrencia, CompraParcelada


app = Flask (__name__)

#Configuração da conexão com banco de dados
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

#Inicialização do banco de dadoss
db.init_app(app)


@app.route("/")
def inicio(): 
    return "Sistema Financeiro - Aplicação em Desenvolvimento e com postgre!!"

if __name__ == "__main__":

        
    with app.app_context():

        # Criação das tabelas
        db.create_all()

        #Teste de conexão
        db.session.execute(text("SELECT 1"))

        print("Conexão com Postgresql realizada com sucesso!")
        print("Tabelas verificadas/criadas com sucesso")


    app.run (debug=True)