# 🍕 Pizza Delivery API

Uma API de gerenciamento de pedidos de delivery desenvolvida com **FastAPI**, **SQLAlchemy** e **PostgreSQL**. O projeto conta com um sistema completo de segurança JWT, controle de permissões por nível de usuário e persistência de dados no **Supabase**.

## Tecnologias Utilizadas

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Banco de Dados:** PostgreSQL (via [Supabase](https://supabase.com/)) & SQLite (Local)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Segurança:**
  - **JWT (JSON Web Tokens):** Para autenticação e autorização segura.
  - **Passlib (Bcrypt):** Para criptografia de senhas no banco de dados.
- **Hospedagem:** [Render](https://render.com/)

## Funcionalidades

### Autenticação e Usuários

- **Registro de Usuários:** Cadastro com e-mail único e senhas protegidas.
- **Sistema de Login:** Geração de `Access Token` e `Refresh Token`.
- **Authorize Swagger:** Suporte nativo ao botão "Authorize" do FastAPI para testes rápidos.
- **Níveis de Acesso:** Distinção entre usuários comuns e administradores.

### Gestão de Pedidos

- **Fluxo Completo:** Criar, visualizar, finalizar e cancelar pedidos.
- **Gestão de Itens:** Adicionar ou remover pizzas (sabor, tamanho e quantidade) em pedidos existentes.
- **Cálculo de Preço:** O sistema recalcula o valor total do pedido automaticamente a cada mudança nos itens.
- **Histórico:** Consulta de pedidos específicos ou listagem geral de pedidos do usuário logado.

## Estrutura do Projeto

- `main.py`: Inicialização da aplicação, roteamento e criação automática de tabelas.
- `models.py`: Definição das tabelas de banco de dados e lógica de cálculo de preço.
- `auth_routes.py`: Endpoints de autenticação, login e criação de contas.
- `order_routes.py`: Lógica de negócio para pedidos e controle de permissões.
- `schemas.py`: Modelos Pydantic para validação de dados de entrada e saída.
- `dependencies.py`: Injeção de dependências para sessões de banco e verificação de tokens.

## Configuração de Ambiente

Para rodar o projeto, as seguintes variáveis de ambiente devem ser configuradas (no arquivo `.env` ou no painel do Render):

| Variável                       | Descrição                                        |
| :----------------------------- | :----------------------------------------------- |
| `DATABASE_URL`                 | Link de conexão com o banco de dados PostgreSQL  |
| `SECRET_KEY`                   | Chave secreta para assinatura dos tokens JWT     |
| `ALGORITHM`                    | Algoritmo de criptografia (Ex: HS256)            |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | Tempo de expiração do token de acesso            |

## Como Utilizar

1. **Acesse a Documentação:**
     Vá para `https://delivery-wd2n.onrender.com/docs`
2. **Crie um Usuário:**
     Utilize a rota `POST /auth/criar_conta`.

3. **Autentique-se:**
     Clique no botão **Authorize** no topo do Swagger, insira seu e-mail e senha.

4. **Faça um Pedido:**
     Utilize as rotas de `/pedidos` para simular o fluxo de compra de uma pizza.
