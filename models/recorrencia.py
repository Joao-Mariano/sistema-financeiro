from extensions import db

class Recorrencia(db.Model):

    __tablename__ = "recorrencia"

    id_recorrencia = db.Column(
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

    periodicidade = db.Column(
        db.String(20),
        nullable=False
    )

    data_inicio = db.Column(
        db.Date,
        nullable=False
    )

    data_fim = db.Column(
        db.Date,
        nullable=True
    )

    ativa = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )