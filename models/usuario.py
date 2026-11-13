from extensions import db

class Usuario(db.Model):

    __tablename__ = "usuario"

    id_usuario = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150), 
        unique=True, 
        nullable=False
    )

    senha_hash = db.Column(
        db.String(255), 
        nullable=False
    )
    
    data_cadastro = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    categorias = db.relationship(
        "Categoria",
        backref="usuario",
        lazy=True
    )

    receitas = db.relationship(
        "Receita",
        back_populates="usuario",
        lazy=True
    )

    recorrencias = db.relationship(
        "Recorrencia",
        back_populates="usuario",
        lazy=True
    )

    compras_parceladas = db.relationship(
        "CompraParcelada",
        back_populates="usuario",
        lazy=True
    )

    despesas = db.relationship(
        "Despesa",
        back_populates="usuario",
        lazy=True
    )
    