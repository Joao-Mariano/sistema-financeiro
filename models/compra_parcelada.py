from extensions import db

class CompraParcelada(db.Model):
    
    __tablename__ = "compra_parcelada"

    id_compra_parcelada = db.Column(
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

    valor_total = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    quantidade_parcelas = db.Column(
        db.Integer,
        nullable=False
    )

    data_primeiro_vencimento = db.Column(
        db.Date,
        nullable=False
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

    usuario = db.relationship(
        "Usuario",
        back_populates="compras_parceladas"
    )

    despesas = db.relationship(
        "Despesa",
        back_populates="compra_parcelada",
        lazy=True
    )

    categoria = db.relationship(
        "Categoria",
        back_populates="compras_parceladas"
    )
    