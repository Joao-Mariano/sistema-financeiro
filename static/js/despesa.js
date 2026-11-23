document.addEventListener("DOMContentLoaded", function () {

    const elementoCategorias = document.getElementById("dados-categorias");

    const categoriasDespesa = JSON.parse(
        elementoCategorias.dataset.categorias
    );

    const opcoes = document.querySelectorAll(".opcao-despesa");
    const areaFormulario = document.getElementById("area-formulario");
    const tituloFormulario = document.getElementById("titulo-formulario");
    const conteudoFormulario = document.getElementById("conteudo-formulario");

    const formularios = {

        normal: {
            titulo: "Cadastrar despesa normal",
            mensagem: `
                <form
                    id="form-despesa-normal"
                    method="POST"
                    action="/despesas">

                    <div class="campo-formulario">
                        <label for="descricao">Descrição</label>
                        <input
                            type="text"
                            id="descricao"
                            name="descricao"
                            maxlength="150"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="categoria">Categoria</label>
                        <select id="categoria" name="id_categoria" required>
                            <option value="">Selecione uma categoria</option>
                            ${categoriasDespesa.map(categoria => `
                                <option value="${categoria.id}">
                                    ${categoria.nome}
                                </option>
                            `).join("")}
                        </select>
                    </div>

                    <div class="campo-formulario">
                        <label for="valor">Valor (R$)</label>
                        <input
                            type="number"
                            id="valor"
                            name="valor"
                            min="0.01"
                            step="0.01"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="data_vencimento">Data de vencimento</label>
                        <input
                            type="date"
                            id="data_vencimento"
                            name="data_vencimento"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="status">Status</label>
                        <select id="status" name="status" required>
                            <option value="PENDENTE">Pendente</option>
                            <option value="PAGA">Paga</option>
                        </select>
                    </div>

                    <button type="submit" class="btn-cadastrar">
                        Cadastrar despesa
                    </button>

                </form>
            `
        },

        recorrente: {
            titulo: "Cadastrar despesa recorrente",
            mensagem: `
                <form
                    id="form-despesa-recorrente"
                    method="POST"
                    action="/despesas/recorrente">

                    <div class="campo-formulario">
                        <label for="descricao_recorrente">Descrição</label>
                        <input
                            type="text"
                            id="descricao_recorrente"
                            name="descricao"
                            maxlength="150"
                            placeholder="Ex.: Aluguel"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="categoria_recorrente">Categoria</label>
                        <select
                            id="categoria_recorrente"
                            name="id_categoria"
                            required>

                            <option value="">Selecione uma categoria</option>

                            ${categoriasDespesa.map(categoria => `
                                <option value="${categoria.id}">
                                    ${categoria.nome}
                                </option>
                            `).join("")}

                        </select>
                    </div>

                    <div class="campo-formulario">
                        <label for="valor_recorrente">Valor (R$)</label>
                        <input
                            type="number"
                            id="valor_recorrente"
                            name="valor"
                            min="0.01"
                            step="0.01"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="periodicidade">Periodicidade</label>
                        <select
                            id="periodicidade"
                            name="periodicidade"
                            required>

                            <option value="">Selecione a periodicidade</option>
                            <option value="DIARIA">Diária</option>
                            <option value="SEMANAL">Semanal</option>
                            <option value="QUINZENAL">Quinzenal</option>
                            <option value="MENSAL">Mensal</option>
                            <option value="BIMESTRAL">Bimestral</option>
                            <option value="TRIMESTRAL">Trimestral</option>
                            <option value="SEMESTRAL">Semestral</option>
                            <option value="ANUAL">Anual</option>

                        </select>
                    </div>

                    <div class="campo-formulario">
                        <label for="data_inicio">Data de início</label>
                        <input
                            type="date"
                            id="data_inicio"
                            name="data_inicio"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="data_fim">Data de término (opcional)</label>
                        <input
                            type="date"
                            id="data_fim"
                            name="data_fim">
                    </div>

                    <button type="submit" class="btn-cadastrar">
                        Cadastrar recorrência
                    </button>

                </form>
            `
        },

        parcelada: {
            titulo: "Cadastrar compra parcelada",
            mensagem: `
                <form
                    id="form-compra-parcelada"
                    method="POST"
                    action="/despesas/parcelada">

                    <div class="campo-formulario">
                        <label for="descricao_parcelada">Descrição</label>
                        <input
                            type="text"
                            id="descricao_parcelada"
                            name="descricao"
                            maxlength="150"
                            placeholder="Ex.: Notebook"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="categoria_parcelada">Categoria</label>
                        <select
                            id="categoria_parcelada"
                            name="id_categoria"
                            required>

                            <option value="">Selecione uma categoria</option>

                            ${categoriasDespesa.map(categoria => `
                                <option value="${categoria.id}">
                                    ${categoria.nome}
                                </option>
                            `).join("")}

                        </select>
                    </div>

                    <div class="campo-formulario">
                        <label for="valor_total">Valor total (R$)</label>
                        <input
                            type="number"
                            id="valor_total"
                            name="valor_total"
                            min="0.01"
                            step="0.01"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="quantidade_parcelas">Quantidade de parcelas</label>
                        <input
                            type="number"
                            id="quantidade_parcelas"
                            name="quantidade_parcelas"
                            min="1"
                            step="1"
                            required>
                    </div>

                    <div class="campo-formulario">
                        <label for="data_primeiro_vencimento">Data do primeiro vencimento</label>
                        <input
                            type="date"
                            id="data_primeiro_vencimento"
                            name="data_primeiro_vencimento"
                            required>
                    </div>

                    <button type="submit" class="btn-cadastrar">
                        Cadastrar compra parcelada
                    </button>

                </form>
            `
        }

    };

    opcoes.forEach(function (opcao) {

        opcao.addEventListener("click", function () {

            const tipo = opcao.dataset.tipo;
            const formulario = formularios[tipo];

            opcoes.forEach(function (item) {
                item.classList.remove("selecionada");
            });

            opcao.classList.add("selecionada");

            tituloFormulario.textContent = formulario.titulo;

            conteudoFormulario.innerHTML = `
                <p class="mensagem-formulario">
                    ${formulario.mensagem}
                </p>
            `;

            areaFormulario.style.display = "block";

        });

    });


    // Edição de despesas
document.addEventListener("click", function(event) {

    const botaoEditar = event.target.closest(".btn-editar-despesa");

    if (botaoEditar) {
        const id = botaoEditar.dataset.id;

        const formulario = document.getElementById(
            "form-edicao-despesa-" + id
        );

        formulario.style.display = "table-row";

        const campoStatus = formulario.querySelector(".campo-status-edicao");

        if (campoStatus) {
            campoStatus.style.display = "";
            campoStatus.querySelector("select").disabled = false;
        }
    }

    const botaoFechar = event.target.closest(".btn-fechar-edicao");

    if (botaoFechar) {
        const id = botaoFechar.dataset.id;

        document.getElementById(
            "form-edicao-despesa-" + id
        ).style.display = "none";
    }

    const botaoProximas = event.target.closest(".btn-salvar-proximas");

    if (botaoProximas) {

            const botaoIndividual = event.target.closest(
                ".btn-salvar-despesa:not(.btn-salvar-proximas)"
            );

            if (botaoIndividual) {
                const formulario = botaoIndividual.closest("form");

                const campoStatus = formulario.querySelector(".campo-status-edicao");

                if (campoStatus) {
                    campoStatus.style.display = "";
                    campoStatus.querySelector("select").disabled = false;
                }
            }

        const formulario = botaoProximas.closest("form");

        const campoStatus = formulario.querySelector(".campo-status-edicao");

        if (campoStatus) {
            campoStatus.style.display = "none";
            campoStatus.querySelector("select").disabled = true;
        }
    }
});
});
