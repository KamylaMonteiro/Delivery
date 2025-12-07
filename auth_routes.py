from fastapi import APIRouter
from models import Usuario, db
from sqlalchemy.orm import sessionmaker

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home ():
  """
  Essa é a rota padrão de autenticação do sistema
  """
  return {"mensagem: você acessou a rota padrão de autenticação", "autenticado: False"}

@auth_router.post("/criar_conta")
async def criar_conta(email: str, senha: str, nome: str):
  Session = sessionmaker(bind=db)
  session = Session()
  usuario = session.query(Usuario).filter(Usuario.email==email).first()
  if usuario:
    return {"Já existe um usuário com esse email"}

  else:
    novo_usuario = Usuario(nome, email, senha)
    session.add(novo_usuario)
    session.commit()
    return {"Usuário cadastrado com sucesso"}


