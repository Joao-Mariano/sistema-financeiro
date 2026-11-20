from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models.usuario import Usuario
from models.despesa import Despesa
from models.receita import Receita
from models.categoria import Categoria

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, Numeric

from datetime import date
from decimal import Decimal, InvalidOperation


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")


        if not nome or not email or not senha or not confirmar_senha:
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("auth.cadastro"))

        
        if len(nome) > 100:
            flash("O nome deve ter no máximo 100 caracteres.", "danger")
            return redirect(url_for("auth.cadastro"))

        
        if len(email) > 150:
            flash("O e-mail deve ter no máximo 150 caracteres.", "danger")
            return redirect(url_for("auth.cadastro"))

        
        if len(senha) < 8:
            flash("A senha deve possuir pelo menos 8 caracteres.", "danger")
            return redirect(url_for("auth.cadastro"))

        
        if senha != confirmar_senha:
            flash("As senhas informadas não coincidem.", "danger")
            return redirect(url_for("auth.cadastro"))

        
        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("Este e-mail já está cadastrado.", "danger")
            return redirect(url_for("auth.cadastro"))

        
        senha_hash = generate_password_hash(senha)

        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=senha_hash
        )

        try:

            db.session.add(novo_usuario)
            db.session.commit()

        except IntegrityError:

            db.session.rollback()

            flash("Não foi possível cadastrar. Verifique os dados informados.", "danger")
            return redirect(url_for("auth.cadastro"))

        flash("Cadastro realizado com sucesso!", "success")

        return redirect(url_for("auth.login"))

    return render_template("cadastro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        
        if not email or not senha:
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("auth.login"))

        
        usuario = Usuario.query.filter_by(email=email).first()

        
        if usuario and check_password_hash(usuario.senha_hash, senha):

            login_user(usuario)

            flash("Login realizado com sucesso!", "success")

            return redirect(url_for("auth.dashboard"))

        flash("E-mail ou senha incorretos.", "danger")

        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/dashboard")
@login_required
def dashboard():

    total_receitas = db.session.query(
        func.coalesce(func.sum(Receita.valor), 0)
    ).filter(
        Receita.id_usuario == current_user.id_usuario,
        Receita.status == "RECEBIDA"
    ).scalar()

    
    total_despesas = db.session.query(
        func.coalesce(func.sum(Despesa.valor), 0)
    ).filter(
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.status == "PAGA"
    ).scalar()

    
    saldo_atual = total_receitas - total_despesas

    proximas_contas = Despesa.query.filter(
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.status == "PENDENTE"
    ).order_by(
        Despesa.data_vencimento.asc()
    ).limit(5).all()

    hoje = date.today()

    return render_template(
        "dashboard.html",
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        saldo_atual=saldo_atual,
        proximas_contas=proximas_contas,
        hoje=hoje
    )

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("Você saiu da sua conta.", "success")

    return redirect(url_for("auth.login"))

@auth_bp.route("/categorias", methods=["GET", "POST"])
@login_required
def categorias():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        tipo = request.form.get("tipo", "").strip()

        
        if not nome or not tipo:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("auth.categorias"))

        
        if len(nome) > 100:
            flash("O nome da categoria deve ter no máximo 100 caracteres.", "erro")
            return redirect(url_for("auth.categorias"))

        
        if tipo not in ["RECEITA", "DESPESA"]:
            flash("Tipo de categoria inválido.", "erro")
            return redirect(url_for("auth.categorias"))

        
        categoria_existente = Categoria.query.filter(
            Categoria.id_usuario == current_user.id_usuario,
            func.lower(Categoria.nome) == nome.lower(),
            Categoria.tipo == tipo
        ).first()

        if categoria_existente:

            if categoria_existente.ativa:
                flash(
                    "Você já possui uma categoria ativa com esse nome e tipo.",
                    "erro"
                )
                return redirect(url_for("auth.categorias"))

            else:
                flash(
                    "Essa categoria já existe, mas está desativada. "
                    "Você pode reativá-la na lista de categorias.",
                    "erro"
                )
                return redirect(url_for("auth.categorias"))

        
        nova_categoria = Categoria(
            id_usuario=current_user.id_usuario,
            nome=nome,
            tipo=tipo
        )

        db.session.add(nova_categoria)
        db.session.commit()

        flash("Categoria cadastrada com sucesso!", "sucesso")

        return redirect(url_for("auth.categorias"))

    
    lista_categorias = Categoria.query.filter_by(
        id_usuario=current_user.id_usuario
    ).order_by(Categoria.nome.asc()).all()

    return render_template(
        "categoria.html",
        categorias=lista_categorias
    )


@auth_bp.route("/categorias/desativar/<int:id_categoria>", methods=["POST"])
@login_required
def desativar_categoria(id_categoria):

    
    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario
    ).first_or_404()

    
    if not categoria.ativa:
        flash("Esta categoria já está desativada.", "erro")
        return redirect(url_for("auth.categorias"))

    
    categoria.ativa = False

    db.session.commit()

    flash("Categoria desativada com sucesso!", "sucesso")

    return redirect(url_for("auth.categorias"))


@auth_bp.route("/categorias/reativar/<int:id_categoria>", methods=["POST"])
@login_required
def reativar_categoria(id_categoria):

    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario
    ).first_or_404()

    if categoria.ativa:
        flash("Esta categoria já está ativa.", "erro")
        return redirect(url_for("auth.categorias"))

    categoria.ativa = True

    db.session.commit()

    flash("Categoria reativada com sucesso!", "sucesso")

    return redirect(url_for("auth.categorias"))


@auth_bp.route("/categorias/editar/<int:id_categoria>", methods=["POST"])
@login_required
def editar_categoria(id_categoria):

    
    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario
    ).first_or_404()

    novo_nome = request.form.get("nome", "").strip()

    
    if not novo_nome:
        flash("O nome da categoria é obrigatório.", "erro")
        return redirect(url_for("auth.categorias"))

    
    if len(novo_nome) > 100:
        flash("O nome da categoria deve ter no máximo 100 caracteres.", "erro")
        return redirect(url_for("auth.categorias"))


    # duplicidade
    categoria_existente = Categoria.query.filter(
        Categoria.id_usuario == current_user.id_usuario,
        Categoria.id_categoria != categoria.id_categoria,
        func.lower(Categoria.nome) == novo_nome.lower(),
        Categoria.tipo == categoria.tipo
    ).first()

    if categoria_existente:
        flash(
            "Você já possui outra categoria com esse nome e tipo.",
            "erro"
        )
        return redirect(url_for("auth.categorias"))

    
    categoria.nome = novo_nome

    db.session.commit()

    flash("Categoria atualizada com sucesso!", "sucesso")

    return redirect(url_for("auth.categorias"))


@auth_bp.route("/receitas", methods=["GET", "POST"])
@login_required
def receitas():

    if request.method == "POST":

        descricao = request.form.get("descricao", "").strip()
        id_categoria = request.form.get("id_categoria", "")
        valor = request.form.get("valor", "")
        data_recebimento = request.form.get("data_recebimento", "")
        status = request.form.get("status", "")

        
        if not all([descricao, id_categoria, valor, data_recebimento, status]):
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("auth.receitas"))

        
        if len(descricao) > 150:
            flash("A descrição deve ter no máximo 150 caracteres.", "erro")
            return redirect(url_for("auth.receitas"))

        try:
            id_categoria = int(id_categoria)
        except (ValueError, TypeError):
            flash("Selecione uma categoria válida.", "erro")
            return redirect(url_for("auth.receitas"))

        
        try:
            valor = Decimal(valor.replace(",", "."))
        except (InvalidOperation, ValueError):
            flash("Informe um valor válido.", "erro")
            return redirect(url_for("auth.receitas"))


        if not valor.is_finite() or valor <= 0:
            flash("O valor deve ser maior que zero.", "erro")
            return redirect(url_for("auth.receitas"))

        
        try:
            data_recebimento = date.fromisoformat(data_recebimento)
        except ValueError:
            flash("Informe uma data válida.", "erro")
            return redirect(url_for("auth.receitas"))

        
        if status not in ["PENDENTE", "RECEBIDA"]:
            flash("Status inválido.", "erro")
            return redirect(url_for("auth.receitas"))

        
        categoria = Categoria.query.filter_by(
            id_categoria=id_categoria,
            id_usuario=current_user.id_usuario,
            tipo="RECEITA",
            ativa=True
        ).first()


        if not categoria:
            flash("Selecione uma categoria de receita válida.", "erro")
            return redirect(url_for("auth.receitas"))

        
        nova_receita = Receita(
            id_usuario=current_user.id_usuario,
            id_categoria=categoria.id_categoria,
            descricao=descricao,
            valor=valor,
            data_recebimento=data_recebimento,
            status=status
        )

        db.session.add(nova_receita)
        db.session.commit()

        flash("Receita cadastrada com sucesso!", "sucesso")

        return redirect(url_for("auth.receitas"))

    
    categorias = Categoria.query.filter_by(
        id_usuario=current_user.id_usuario,
        tipo="RECEITA",
        ativa=True
    ).order_by(Categoria.nome.asc()).all()

    lista_receitas = Receita.query.filter_by(
        id_usuario=current_user.id_usuario
    ).order_by(Receita.data_recebimento.desc()).all()

    return render_template(
        "receita.html",
        categorias=categorias,
        receitas=lista_receitas
    )



@auth_bp.route("/receitas/editar/<int:id_receita>", methods=["POST"])
@login_required
def editar_receita(id_receita):

    receita = Receita.query.filter_by(
        id_receita=id_receita,
        id_usuario=current_user.id_usuario
    ).first_or_404()

    descricao = request.form.get("descricao", "").strip()
    id_categoria = request.form.get("id_categoria", "")
    valor = request.form.get("valor", "")
    data_recebimento = request.form.get("data_recebimento", "")
    status = request.form.get("status", "")

    if not all([descricao, id_categoria, valor, data_recebimento, status]):
        flash("Preencha todos os campos.", "erro")
        return redirect(url_for("auth.receitas"))

    if len(descricao) > 150:
        flash("A descrição deve ter no máximo 150 caracteres.", "erro")
        return redirect(url_for("auth.receitas"))

    try:
        id_categoria = int(id_categoria)
    except (ValueError, TypeError):
        flash("Selecione uma categoria válida.", "erro")
        return redirect(url_for("auth.receitas"))

    try:
        valor = Decimal(valor.replace(",", "."))
    except (InvalidOperation, ValueError):
        flash("Informe um valor válido.", "erro")
        return redirect(url_for("auth.receitas"))

    if not valor.is_finite() or valor <= 0:
        flash("O valor deve ser maior que zero.", "erro")
        return redirect(url_for("auth.receitas"))

    try:
        data_recebimento = date.fromisoformat(data_recebimento)
    except ValueError:
        flash("Informe uma data válida.", "erro")
        return redirect(url_for("auth.receitas"))

    if status not in ["PENDENTE", "RECEBIDA"]:
        flash("Status inválido.", "erro")
        return redirect(url_for("auth.receitas"))

    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario,
        tipo="RECEITA",
        ativa=True
    ).first()

    if not categoria:
        flash("Selecione uma categoria de receita válida.", "erro")
        return redirect(url_for("auth.receitas"))

    receita.descricao = descricao
    receita.id_categoria = categoria.id_categoria
    receita.valor = valor
    receita.data_recebimento = data_recebimento
    receita.status = status

    db.session.commit()

    flash("Receita atualizada com sucesso!", "sucesso")
    return redirect(url_for("auth.receitas"))



@auth_bp.route("/receitas/excluir/<int:id_receita>", methods=["POST"])
@login_required
def excluir_receita(id_receita):

    receita = Receita.query.filter_by(
        id_receita=id_receita,
        id_usuario=current_user.id_usuario
    ).first_or_404()

    db.session.delete(receita)
    db.session.commit()

    flash("Receita excluída com sucesso!", "sucesso")

    return redirect(url_for("auth.receitas"))