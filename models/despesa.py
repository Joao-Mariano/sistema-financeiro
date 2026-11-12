from extensions import db

class Despesa(db.Model):

    __tablename__ = "despesa"

    id_despesa = db.Column(
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

    id_recorrencia = db.Column(
        db.Integer,
        db.ForeignKey("recorrencia.id_recorrencia"),
        nullable=True
    )

    id_compra_parcelada = db.Column(
        db.Integer,
        db.ForeignKey("compra_parcelada.id_compra_parcelada"),
        nullable=True
    )

    descricao = db.Column(
        db.String(150),
        nullable=False
    )

    valor = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    data_vencimento = db.Column(
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