Sistema Financeiro

Sistema web de gerenciamento financeiro pessoal, desenvolvido como projeto acadêmico do curso de Análise e Desenvolvimento de Sistemas (ADS).

A aplicação permite que usuários organizem suas finanças pessoais, acompanhem receitas e despesas, controlem contas futuras e visualizem um resumo de sua situação financeira.

## Funcionalidades

Usuários

- Cadastro de usuários.
- Login e autenticação.
- Visualização de dados pessoais.
- Exclusão de conta.

Receitas

- Cadastro de receitas.
- Edição e exclusão de registros.
- Controle de status: pendente e recebida.
- Organização por categorias.

Despesas

- Cadastro e gerenciamento de despesas.
- Cadastro de despesas recorrentes.
- Cadastro de compras parceladas.
- Geração automática de despesas futuras.
- Controle de vencimentos e pagamentos.
- Cancelamento de despesas pendentes.
- Consulta de despesas em uma listagem unificada.

Dashboard

- Visualização do saldo atual.
- Resumo de receitas recebidas.
- Resumo de despesas pagas.
- Gráfico comparativo de receitas e despesas.
- Visualização das próximas contas.

Categorias

- Cadastro de categorias.
- Organização de receitas e despesas.
- Desativação de categorias.

Tecnologias utilizadas

**Backend**

- Python
- Flask
- Flask-SQLAlchemy

**Frontend**

- HTML5
- CSS3
- JavaScript
- Bootstrap

## Estrutura do projeto

O projeto está organizado em diretórios e arquivos responsáveis por diferentes partes da aplicação:

- `app.py`: arquivo principal, responsável pela inicialização da aplicação Flask e configuração do banco de dados.
- `models/`: contém os modelos que representam as entidades e tabelas do banco de dados.
- `routes/`: contém as rotas responsáveis pelo processamento das requisições e pelas funcionalidades do sistema.
- `templates/`: contém os arquivos HTML utilizados na interface.
- `static/`: contém os arquivos CSS e JavaScript.
- `extensions.py`: centraliza a configuração de extensões utilizadas pela aplicação.
- `requirements.txt`: lista as dependências necessárias para executar o projeto.
- `.env.example`: apresenta as variáveis de ambiente necessárias para a configuração local.

## Banco de dados

PostgreSQL

## Criação da estrutura do banco de dados

A estrutura do banco de dados é definida por meio dos modelos SQLAlchemy localizados na pasta `models/`. Durante a inicialização da aplicação, o método `db.create_all()` verifica e cria as tabelas necessárias no banco de dados PostgreSQL, caso ainda não existam.

Para executar o sistema, é necessário criar previamente um banco de dados chamado `sistema_financeiro` e configurar os dados de conexão no arquivo `.env`.

**Ferramentas**

- Visual Studio Code
- Git e GitHub
- Lucidchart

## Como executar o projeto

1. Clonar o repositório

git clone https://github.com/Joao-Mariano/sistema-financeiro.git

2. Acessar a pasta

cd sistema-financeiro

3. Criar um ambiente virtual

python -m venv venv

4. Ativar o ambiente virtual

No Windows:

venv\Scripts\activate

5. Instalar as dependências

pip install -r requirements.txt

6. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto, utilizando o `.env.example` como referência.

Configure as variáveis necessárias:

FLASK_SECRET_KEY=sua_chave_secreta
DB_PASSWORD=sua_senha_do_postgresql

7.  Configurar o banco de dados

Instale e inicie o PostgreSQL.

Crie um banco de dados chamado:

sistema_financeiro

Confira as configurações de conexão no arquivo `app.py` e ajuste-as conforme seu ambiente.

8.  Executar a aplicação

python app.py

A aplicação estará disponível localmente em:

http://127.0.0.1:5000

## Projeto acadêmico

Projeto desenvolvido para fins acadêmicos no curso de Análise e Desenvolvimento de Sistemas (ADS).
