from extensions import db

class Categoria(db.Model):

    __tablename__ = "categoria"

    id_categoria = db.Column(db.Integer, primary_key=True)

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    nome = db.Column(db.String(100), nullable=False)

    tipo = db.Column(db.String(10), nullable=False)

    ativa = db.Column(db.Boolean, nullable=False, default=True)
    
    data_criação = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )
