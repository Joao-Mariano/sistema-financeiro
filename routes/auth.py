from flask import Blueprint, render_template, request, redirect, url_for, flash

from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models.usuario import Usuario
from models.despesa import Despesa
from models.receita import Receita

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.exc import IntegrityError

from sqlalchemy import func, Numeric

from datetime import date


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