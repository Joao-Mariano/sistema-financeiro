from extensions import db

class Receita(db.Model):

    __tablename__ = "receita"

    id_receita = db.Column(
        db.Integer,
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    id_categoria = db.Column(
        db.Integer,
        db.ForeignKey("categoria.id_categoria"),
        nullable=False
    )

    descricao = db.Column(
        db.String(150),
        nullable=False
    )

    valor = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    data_recebimento = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(10),
        nullable=False,
        default="PENDENTE"
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )