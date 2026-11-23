from extensions import db
from sqlalchemy import UniqueConstraint

class Despesa(db.Model):

    __tablename__ = "despesa"

    __table_args__ = (
        UniqueConstraint(
            "id_recorrencia",
            "data_vencimento",
            name="uq_despesa_recorrencia_vencimento"
        ),
    )

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

    numero_parcela = db.Column(
        db.Integer,
        nullable=True
    )

    total_parcelas = db.Column(
        db.Integer,
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

    categoria = db.relationship(
        "Categoria",
        back_populates="despesas"
    )

    recorrencia = db.relationship(
        "Recorrencia",
        back_populates="despesas"
    )

    compra_parcelada = db.relationship(
        "CompraParcelada",
        back_populates="despesas"
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="despesas"
    )
    