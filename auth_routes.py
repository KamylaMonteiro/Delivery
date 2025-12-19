from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
  data_expiracao = datetime.now(timezone.utc) + duracao_token
  dic_info = {"sub": str (id_usuario), "exp": data_expiracao}
  jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
  return jwt_codificado

def autenticar_usuario(email, senha, session):
  usuario = session.query(Usuario).filter(Usuario.email==email).first()
  if not usuario:
    return False
  elif not bcrypt_context.verify(senha, usuario.senha):
    return False
  return usuario

@auth_router.get("/")
async def autenticar():
  """
  Essa é a rota padrão de autenticação do sistema
  """
  return {"mensagem": "você acessou a rota padrão de autenticação", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schemas: UsuarioSchema, session: Session=Depends(pegar_sessao)):
  """
  Cria um novo usuário no sistema e retorna o ID do seu usuário.
  
  Este ID será necessário para operações de pedidos.
  """

  usuario = session.query(Usuario).filter(Usuario.email==usuario_schemas.email).first()
  if usuario:
    raise HTTPException (status_code=400, detail="E-mail já cadastrado")
  
  else:
    senha_criptografada = bcrypt_context.hash(usuario_schemas.senha)
    novo_usuario = Usuario(usuario_schemas.nome, usuario_schemas.email, senha_criptografada, usuario_schemas.ativo, usuario_schemas.admin)
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)

    return {
        "mensagem": "Usuário cadastrado com sucesso",
        "usuario_id": novo_usuario.id,
        "email": novo_usuario.email
    }

@auth_router.post("/login")
async def login(login_schemas: LoginSchema, session: Session=Depends(pegar_sessao)):
  """
  Autentica o usuário via e-mail e senha.
  
  Retorna um Access Token JWT e um Refresh Token.
  """
  usuario = autenticar_usuario(login_schemas.email, login_schemas.senha, session)
  if not usuario:
    raise HTTPException (status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
  else:
    access_token = criar_token(usuario.id)
    refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
    return {"access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type":"Bearer"
            }
  
@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session=Depends(pegar_sessao)):
  """
  Autenticação compatível com o botão 'Authorize' do Swagger UI.
  """
  usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
  if not usuario:
    raise HTTPException (status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
  else:
    access_token = criar_token(usuario.id)
    return {"access_token": access_token, 
            "token_type":"Bearer"
            }
  
@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
  """
  Gera um novo Access Token válido utilizando um token existente
  
  Permite manter o usuário conectado sem exigir novo login imediato.
  """
  access_token = criar_token(usuario.id)
  return {
      "access_token": access_token,
      "token_type":"Bearer"
      }