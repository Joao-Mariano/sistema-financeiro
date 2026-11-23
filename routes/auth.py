from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from services.recorrencia_service import gerar_despesas_recorrentes, calcular_proximo_vencimento

from extensions import db
from models.usuario import Usuario
from models.despesa import Despesa
from models.receita import Receita
from models.categoria import Categoria
from models.recorrencia import Recorrencia
from models.compra_parcelada import CompraParcelada

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, Numeric

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_DOWN

import secrets
import hmac
from flask import session


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



@auth_bp.route("/minha-conta")
@login_required
def minha_conta():
    return render_template("minha_conta.html")



@auth_bp.route("/excluir-conta", methods=["GET", "POST"])
@login_required
def excluir_conta():

    if request.method == "POST":

        token = request.form.get("csrf_token", "")
        token_sessao = session.get("csrf_token")

        if not token_sessao or not hmac.compare_digest(token, token_sessao):
            flash("Solicitação inválida. Tente novamente.", "erro")
            return redirect(url_for("auth.excluir_conta"))

        senha = request.form.get("senha", "")

        if not check_password_hash(current_user.senha_hash, senha):
            flash("Senha incorreta.", "erro")
            return redirect(url_for("auth.excluir_conta"))

        try:
            id_usuario = current_user.id_usuario

            Despesa.query.filter_by(id_usuario=id_usuario).delete(
                synchronize_session=False
            )

            Receita.query.filter_by(id_usuario=id_usuario).delete(
                synchronize_session=False
            )

            Recorrencia.query.filter_by(id_usuario=id_usuario).delete(
                synchronize_session=False
            )

            CompraParcelada.query.filter_by(id_usuario=id_usuario).delete(
                synchronize_session=False
            )

            Categoria.query.filter_by(id_usuario=id_usuario).delete(
                synchronize_session=False
            )

            Usuario.query.filter_by(id_usuario=id_usuario).delete(
                synchronize_session=False
            )

            db.session.commit()

            logout_user()
            session.clear()

            flash("Sua conta foi excluída com sucesso.", "sucesso")
            return redirect(url_for("auth.login"))

        except Exception as erro:
            db.session.rollback()
            print("Erro ao excluir conta:", erro)

            flash("Não foi possível excluir sua conta.", "erro")
            return redirect(url_for("auth.excluir_conta"))

    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token

    return render_template(
        "excluir_conta.html",
        csrf_token=token
    )


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



@auth_bp.route("/despesas", methods=["GET", "POST"])
@login_required
def despesas():

    if request.method == "POST":

        descricao = request.form.get("descricao", "").strip()
        id_categoria = request.form.get("id_categoria", "")
        valor = request.form.get("valor", "")
        data_vencimento = request.form.get("data_vencimento", "")
        status = request.form.get("status", "")

        if not all([descricao, id_categoria, valor, data_vencimento, status]):
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("auth.despesas"))

        if len(descricao) > 150:
            flash("A descrição deve ter no máximo 150 caracteres.", "erro")
            return redirect(url_for("auth.despesas"))

        try:
            id_categoria = int(id_categoria)
        except (ValueError, TypeError):
            flash("Selecione uma categoria válida.", "erro")
            return redirect(url_for("auth.despesas"))

        try:
            valor = Decimal(valor.replace(",", "."))
        except (InvalidOperation, ValueError):
            flash("Informe um valor válido.", "erro")
            return redirect(url_for("auth.despesas"))

        if not valor.is_finite() or valor <= 0:
            flash("O valor deve ser maior que zero.", "erro")
            return redirect(url_for("auth.despesas"))

        if valor != valor.quantize(Decimal("0.01")):
            flash("O valor deve possuir no máximo duas casas decimais.", "erro")
            return redirect(url_for("auth.despesas"))

        try:
            data_vencimento = date.fromisoformat(data_vencimento)
        except ValueError:
            flash("Informe uma data válida.", "erro")
            return redirect(url_for("auth.despesas"))

        if status not in ["PENDENTE", "PAGA"]:
            flash("Status inválido.", "erro")
            return redirect(url_for("auth.despesas"))

        categoria = Categoria.query.filter_by(
            id_categoria=id_categoria,
            id_usuario=current_user.id_usuario,
            tipo="DESPESA",
            ativa=True
        ).first()

        if not categoria:
            flash("Selecione uma categoria de despesa válida.", "erro")
            return redirect(url_for("auth.despesas"))

        nova_despesa = Despesa(
            id_usuario=current_user.id_usuario,
            id_categoria=categoria.id_categoria,
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            status=status
        )

        try:
            db.session.add(nova_despesa)
            db.session.commit()

            flash("Despesa cadastrada com sucesso!", "sucesso")

        except Exception as erro:
            db.session.rollback()
            print("Erro ao cadastrar despesa:", erro)
            flash("Não foi possível cadastrar a despesa.", "erro")

        return redirect(url_for("auth.despesas"))

        flash("Despesa cadastrada com sucesso!", "sucesso")
        return redirect(url_for("auth.despesas"))

    categorias = Categoria.query.filter_by(
        id_usuario=current_user.id_usuario,
        tipo="DESPESA",
        ativa=True
    ).order_by(Categoria.nome.asc()).all()

    categorias_json = [
        {
            "id": categoria.id_categoria,
            "nome": categoria.nome
        }
        for categoria in categorias
    ]

    lista_despesas = Despesa.query.filter_by(
        id_usuario=current_user.id_usuario
    ).order_by(Despesa.data_vencimento.asc()).all()

    return render_template(
        "despesa.html",
        categorias=categorias_json,
        despesas=lista_despesas
    )



@auth_bp.route("/despesas/editar/<int:id_despesa>", methods=["POST"])
@login_required
def editar_despesa(id_despesa):

    despesa = Despesa.query.filter(
        Despesa.id_despesa == id_despesa,
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.id_recorrencia.is_(None)
    ).first_or_404()

    if despesa.status != "PENDENTE":
        flash("Somente despesas pendentes podem ser editadas.", "erro")
        return redirect(url_for("auth.despesas"))

    descricao = request.form.get("descricao", "").strip()
    id_categoria = request.form.get("id_categoria", "")
    valor = request.form.get("valor", "")
    data_vencimento = request.form.get("data_vencimento", "")
    status = request.form.get("status", "")

    if not all([descricao, id_categoria, valor, status]):
        flash("Preencha todos os campos.", "erro")
        return redirect(url_for("auth.despesas"))

    if len(descricao) > 150:
        flash("A descrição deve ter no máximo 150 caracteres.", "erro")
        return redirect(url_for("auth.despesas"))

    try:
        id_categoria = int(id_categoria)
    except (ValueError, TypeError):
        flash("Selecione uma categoria válida.", "erro")
        return redirect(url_for("auth.despesas"))

    try:
        valor = Decimal(valor.replace(",", "."))
    except (InvalidOperation, ValueError):
        flash("Informe um valor válido.", "erro")
        return redirect(url_for("auth.despesas"))

    if not valor.is_finite() or valor <= 0:
        flash("O valor deve ser maior que zero.", "erro")
        return redirect(url_for("auth.despesas"))

    if valor != valor.quantize(Decimal("0.01")):
        flash("O valor deve possuir no máximo duas casas decimais.", "erro")
        return redirect(url_for("auth.despesas"))

    if despesa.id_compra_parcelada is None:
        try:
            data_vencimento = date.fromisoformat(data_vencimento)
        except ValueError:
            flash("Informe uma data válida.", "erro")
            return redirect(url_for("auth.despesas"))

    if status not in ["PENDENTE", "PAGA"]:
        flash("Status inválido.", "erro")
        return redirect(url_for("auth.despesas"))

    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario,
        tipo="DESPESA",
        ativa=True
    ).first()

    if not categoria:
        flash("Selecione uma categoria de despesa válida.", "erro")
        return redirect(url_for("auth.despesas"))

    despesa.descricao = descricao
    despesa.id_categoria = categoria.id_categoria
    despesa.valor = valor
    if despesa.id_compra_parcelada is None:
        despesa.data_vencimento = data_vencimento
    despesa.status = status

    try:
        db.session.commit()
        flash("Despesa atualizada com sucesso!", "sucesso")

    except Exception as erro:
        db.session.rollback()
        print("Erro ao atualizar despesa:", erro)
        flash("Não foi possível atualizar a despesa.", "erro")

    return redirect(url_for("auth.despesas"))



@auth_bp.route("/despesas/recorrente/editar/<int:id_despesa>", methods=["POST"])
@login_required
def editar_despesa_recorrente(id_despesa):
   
    despesa = Despesa.query.filter(
        Despesa.id_despesa == id_despesa,
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.id_recorrencia.isnot(None)
    ).first_or_404()

    if not despesa.recorrencia.ativa:
        flash("Não é possível editar lançamentos de uma recorrência cancelada.", "erro")
        return redirect(url_for("auth.despesas"))

    
    if despesa.status != "PENDENTE":
        flash("Somente despesas pendentes podem ser editadas.", "erro")
        return redirect(url_for("auth.despesas"))

    descricao = request.form.get("descricao", "").strip()
    id_categoria = request.form.get("id_categoria", "")
    valor = request.form.get("valor", "")
    status = request.form.get("status", "")

    
    if not all([descricao, id_categoria, valor, status]):
        flash("Preencha todos os campos.", "erro")
        return redirect(url_for("auth.despesas"))

    if status not in ["PENDENTE", "PAGA"]:
        flash("Status inválido.", "erro")
        return redirect(url_for("auth.despesas"))

    if len(descricao) > 150:
        flash("A descrição deve ter no máximo 150 caracteres.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        id_categoria = int(id_categoria)
    except (ValueError, TypeError):
        flash("Selecione uma categoria válida.", "erro")
        return redirect(url_for("auth.despesas"))

    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario,
        tipo="DESPESA",
        ativa=True
    ).first()

    if not categoria:
        flash("Selecione uma categoria de despesa válida.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        valor = Decimal(valor.replace(",", "."))
    except (InvalidOperation, ValueError):
        flash("Informe um valor válido.", "erro")
        return redirect(url_for("auth.despesas"))

    if not valor.is_finite() or valor <= 0:
        flash("O valor deve ser maior que zero.", "erro")
        return redirect(url_for("auth.despesas"))

    if valor != valor.quantize(Decimal("0.01")):
        flash("O valor deve possuir no máximo duas casas decimais.", "erro")
        return redirect(url_for("auth.despesas"))

   
    despesa.descricao = descricao
    despesa.id_categoria = categoria.id_categoria
    despesa.valor = valor
    despesa.status = status

    try:
        db.session.commit()
        flash("Lançamento recorrente atualizado com sucesso!", "sucesso")

    except Exception as erro:
        db.session.rollback()
        print("Erro ao atualizar despesa recorrente:", erro)
        flash("Não foi possível atualizar o lançamento.", "erro")

    return redirect(url_for("auth.despesas"))



@auth_bp.route(
    "/despesas/recorrente/editar-proximas/<int:id_despesa>",
    methods=["POST"]
)
@login_required
def editar_proximas_despesas_recorrentes(id_despesa):

    despesa = Despesa.query.filter(
        Despesa.id_despesa == id_despesa,
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.id_recorrencia.isnot(None)
    ).first_or_404()

    recorrencia = Recorrencia.query.filter_by(
        id_recorrencia=despesa.id_recorrencia,
        id_usuario=current_user.id_usuario
    ).first_or_404()

    if not recorrencia.ativa:
        flash("Não é possível editar uma recorrência cancelada.", "erro")
        return redirect(url_for("auth.despesas"))

    if despesa.status != "PENDENTE":
        flash("Selecione uma despesa pendente para realizar a alteração.", "erro")
        return redirect(url_for("auth.despesas"))

    descricao = request.form.get("descricao", "").strip()
    id_categoria = request.form.get("id_categoria", "")
    valor = request.form.get("valor", "")

    if not descricao or not id_categoria or not valor:
        flash("Preencha todos os campos obrigatórios.", "erro")
        return redirect(url_for("auth.despesas"))

    if len(descricao) > 150:
        flash("A descrição deve ter no máximo 150 caracteres.", "erro")
        return redirect(url_for("auth.despesas"))

    try:
        id_categoria = int(id_categoria)
    except ValueError:
        flash("Categoria inválida.", "erro")
        return redirect(url_for("auth.despesas"))

    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario,
        tipo="DESPESA",
        ativa=True
    ).first()

    if not categoria:
        flash("Selecione uma categoria de despesa válida.", "erro")
        return redirect(url_for("auth.despesas"))

    try:
        valor = Decimal(valor.replace(",", "."))
    except InvalidOperation:
        flash("Informe um valor monetário válido.", "erro")
        return redirect(url_for("auth.despesas"))

    if not valor.is_finite() or valor <= 0:
        flash("O valor deve ser maior que zero.", "erro")
        return redirect(url_for("auth.despesas"))

    if valor != valor.quantize(Decimal("0.01")):
        flash("O valor deve possuir no máximo duas casas decimais.", "erro")
        return redirect(url_for("auth.despesas"))

    data_inicio_alteracao = despesa.data_vencimento

    despesas_futuras = Despesa.query.filter(
        Despesa.id_recorrencia == recorrencia.id_recorrencia,
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.data_vencimento >= data_inicio_alteracao,
        Despesa.status == "PENDENTE"
    ).all()


    if not despesas_futuras:
        flash("Nenhuma despesa pendente encontrada para atualização.", "erro")
        return redirect(url_for("auth.despesas"))

    for despesa_futura in despesas_futuras:
        despesa_futura.descricao = descricao
        despesa_futura.id_categoria = categoria.id_categoria
        despesa_futura.valor = valor

    recorrencia.descricao = descricao
    recorrencia.id_categoria = categoria.id_categoria
    recorrencia.valor = valor

    try:
        db.session.commit()

        flash(
            "Este lançamento e os próximos foram atualizados com sucesso!",
            "sucesso"
        )

    except Exception as erro:
        db.session.rollback()
        print("Erro ao atualizar próximas despesas recorrentes:", erro)

        flash(
            "Não foi possível atualizar os próximos lançamentos.",
            "erro"
        )

    return redirect(url_for("auth.despesas"))



@auth_bp.route("/despesas/cancelar/<int:id_despesa>", methods=["POST"])
@login_required
def cancelar_despesa(id_despesa):

    despesa = Despesa.query.filter(
        Despesa.id_despesa == id_despesa,
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.id_recorrencia.is_(None)
    ).first_or_404()

    if despesa.status != "PENDENTE":
        flash("Somente despesas pendentes podem ser canceladas.", "erro")
        return redirect(url_for("auth.despesas"))

    if despesa.status == "PAGA":
        flash("Não é possível cancelar uma despesa já paga.", "erro")
        return redirect(url_for("auth.despesas"))

    if despesa.status == "CANCELADA":
        flash("Esta despesa já está cancelada.", "erro")
        return redirect(url_for("auth.despesas"))

    try:
        despesa.status = "CANCELADA"
        db.session.commit()

        flash("Despesa cancelada com sucesso!", "sucesso")

    except Exception as erro:
        db.session.rollback()
        print("Erro ao cancelar despesa:", erro)
        flash("Não foi possível cancelar a despesa.", "erro")

    return redirect(url_for("auth.despesas"))



@auth_bp.route("/despesas/recorrente", methods=["POST"])
@login_required
def cadastrar_recorrencia():

    descricao = request.form.get("descricao", "").strip()
    id_categoria = request.form.get("id_categoria", "")
    valor = request.form.get("valor", "")
    periodicidade = request.form.get("periodicidade", "")
    data_inicio = request.form.get("data_inicio", "")
    data_fim = request.form.get("data_fim", "")

    
    if not all([descricao, id_categoria, valor, periodicidade, data_inicio]):
        flash("Preencha todos os campos obrigatórios.", "erro")
        return redirect(url_for("auth.despesas"))

    
    if len(descricao) > 150:
        flash("A descrição deve ter no máximo 150 caracteres.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        id_categoria = int(id_categoria)
    except (ValueError, TypeError):
        flash("Selecione uma categoria válida.", "erro")
        return redirect(url_for("auth.despesas"))

    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario,
        tipo="DESPESA",
        ativa=True
    ).first()


    if not categoria:
        flash("Selecione uma categoria de despesa válida.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        valor = Decimal(valor.replace(",", "."))
    except (InvalidOperation, ValueError):
        flash("Informe um valor válido.", "erro")
        return redirect(url_for("auth.despesas"))


    if not valor.is_finite() or valor <= 0:
        flash("O valor deve ser maior que zero.", "erro")
        return redirect(url_for("auth.despesas"))

    if valor != valor.quantize(Decimal("0.01")):
        flash("O valor deve possuir no máximo duas casas decimais.", "erro")
        return redirect(url_for("auth.despesas"))

    
    periodicidades_permitidas = [
        "DIARIA",
        "SEMANAL",
        "QUINZENAL",
        "MENSAL",
        "BIMESTRAL",
        "TRIMESTRAL",
        "SEMESTRAL",
        "ANUAL"
    ]


    if periodicidade not in periodicidades_permitidas:
        flash("Selecione uma periodicidade válida.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        data_inicio = date.fromisoformat(data_inicio)
    except ValueError:
        flash("Informe uma data de início válida.", "erro")
        return redirect(url_for("auth.despesas"))

    
    if data_fim:
        try:
            data_fim = date.fromisoformat(data_fim)
        except ValueError:
            flash("Informe uma data de término válida.", "erro")
            return redirect(url_for("auth.despesas"))

        if data_fim < data_inicio:
            flash("A data de término não pode ser anterior à data de início.", "erro")
            return redirect(url_for("auth.despesas"))
    else:
        data_fim = None

    
    try:
        nova_recorrencia = Recorrencia(
            id_usuario=current_user.id_usuario,
            id_categoria=categoria.id_categoria,
            descricao=descricao,
            valor=valor,
            periodicidade=periodicidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativa=True
        )

        db.session.add(nova_recorrencia)
        db.session.commit()

    except Exception as erro:
        db.session.rollback()
        print("Erro ao cadastrar recorrência:", erro)
        flash("Não foi possível cadastrar a despesa recorrente.", "erro")
        return redirect(url_for("auth.despesas"))


    try:
        gerar_despesas_recorrentes()
    except Exception as erro:
        print("Erro ao gerar despesas recorrentes:", erro)
        flash(
            "Recorrência cadastrada, mas houve um problema ao gerar suas despesas. Elas serão verificadas novamente.",
            "aviso"
        )
        return redirect(url_for("auth.despesas"))

    flash("Despesa recorrente cadastrada com sucesso!", "sucesso")

    return redirect(url_for("auth.despesas"))



@auth_bp.route("/despesas/recorrente/cancelar/<int:id_recorrencia>", methods=["POST"])
@login_required
def cancelar_recorrencia(id_recorrencia):

    
    recorrencia = Recorrencia.query.filter_by(
        id_recorrencia=id_recorrencia,
        id_usuario=current_user.id_usuario
    ).first_or_404()

    
    if not recorrencia.ativa:
        flash("Esta recorrência já está cancelada.", "erro")
        return redirect(url_for("auth.despesas"))

    hoje = date.today()

    
    recorrencia.ativa = False

    
    despesas_futuras = Despesa.query.filter(
        Despesa.id_recorrencia == recorrencia.id_recorrencia,
        Despesa.id_usuario == current_user.id_usuario,
        Despesa.data_vencimento >= hoje,
        Despesa.status == "PENDENTE"
    ).all()

    
    try:
        for despesa in despesas_futuras:
            despesa.status = "CANCELADA"

        db.session.commit()

        flash(
            "Recorrência cancelada e despesas futuras pendentes canceladas com sucesso!",
            "sucesso"
        )

    except Exception as erro:
        db.session.rollback()
        print("Erro ao cancelar recorrência:", erro)

        flash(
            "Não foi possível cancelar a recorrência.",
            "erro"
        )

    return redirect(url_for("auth.despesas"))



@auth_bp.route("/despesas/parcelada", methods=["POST"])
@login_required
def cadastrar_compra_parcelada():
    descricao = request.form.get("descricao", "").strip()
    id_categoria = request.form.get("id_categoria", "").strip()
    valor_total = request.form.get("valor_total", "").strip()
    quantidade_parcelas = request.form.get("quantidade_parcelas", "").strip()
    data_primeiro_vencimento = request.form.get("data_primeiro_vencimento", "").strip()

   
    if not descricao or len(descricao) > 150:
        flash("Informe uma descrição válida.", "erro")
        return redirect(url_for("auth.despesas"))

   
    try:
        id_categoria = int(id_categoria)
    except (ValueError, TypeError):
        flash("Selecione uma categoria válida.", "erro")
        return redirect(url_for("auth.despesas"))

    categoria = Categoria.query.filter_by(
        id_categoria=id_categoria,
        id_usuario=current_user.id_usuario,
        tipo="DESPESA",
        ativa=True
    ).first()

    if not categoria:
        flash("Categoria inválida ou indisponível.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        valor_total = Decimal(valor_total)
        if not valor_total.is_finite() or valor_total <= 0:
            raise InvalidOperation
        if valor_total != valor_total.quantize(Decimal("0.01")):
            flash("O valor deve possuir no máximo duas casas decimais.", "erro")
            return redirect(url_for("auth.despesas"))
    except (InvalidOperation, ValueError):
        flash("Informe um valor total válido.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        quantidade_parcelas = int(quantidade_parcelas)
        if quantidade_parcelas < 1 or quantidade_parcelas > 120:
            raise ValueError
    except ValueError:
        flash("A quantidade deve estar entre 1 e 120 parcelas.", "erro")
        return redirect(url_for("auth.despesas"))

    
    try:
        data_primeiro_vencimento = date.fromisoformat(
            data_primeiro_vencimento
        )
    except ValueError:
        flash("Informe uma data de vencimento válida.", "erro")
        return redirect(url_for("auth.despesas"))

    
    valor_parcela = (
        valor_total / quantidade_parcelas
    ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    try:
        
        nova_compra = CompraParcelada(
            id_usuario=current_user.id_usuario,
            id_categoria=id_categoria,
            descricao=descricao,
            valor_total=valor_total,
            quantidade_parcelas=quantidade_parcelas,
            data_primeiro_vencimento=data_primeiro_vencimento,
            ativa=True
        )

        db.session.add(nova_compra)
        db.session.flush()

        
        for numero in range(1, quantidade_parcelas + 1):

            valor_atual = valor_parcela

            
            if numero == quantidade_parcelas:
                valor_atual = valor_total - (
                    valor_parcela * (quantidade_parcelas - 1)
                )

            data_vencimento = calcular_proximo_vencimento(
                data_primeiro_vencimento,
                "MENSAL",
                numero - 1
            )

            nova_despesa = Despesa(
                id_usuario=current_user.id_usuario,
                id_categoria=id_categoria,
                id_compra_parcelada=nova_compra.id_compra_parcelada,
                descricao=descricao,
                valor=valor_atual,
                data_vencimento=data_vencimento,
                numero_parcela=numero,
                total_parcelas=quantidade_parcelas,
                status="PENDENTE"
            )

            db.session.add(nova_despesa)

        db.session.commit()

        flash(
            f"Compra parcelada cadastrada com sucesso! "
            f"Foram geradas {quantidade_parcelas} parcelas.",
            "sucesso"
        )

    except Exception as erro:
        db.session.rollback()
        print("Erro ao cadastrar compra parcelada:", erro)
        flash("Não foi possível cadastrar a compra parcelada.", "erro")

    return redirect(url_for("auth.despesas"))