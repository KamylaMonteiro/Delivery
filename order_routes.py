from fastapi import APIRouter, Depends, HTTPException
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from sqlalchemy.orm import Session
from models import Pedido, Usuario, ItemPedido
from typing import List

order_router= APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
 
  """Essa é a rota padrão de pedidos do sistema. Todas as rotas dos pedidos precisam de autenticação"""
  return {"mensagem": "você acessou a rota de pedidos"}

@order_router.post("/pedido")
async def criar_pedido (pedido_schemas: PedidoSchema, session: Session=Depends(pegar_sessao)):
  """
  Inicia um novo pedido no sistema.
    
  O pedido será criado com o status inicial 'PENDENTE' e vinculado ao ID do usuário fornecido.
  """
  novo_pedido = Pedido(usuario=pedido_schemas.usuario)
  session.add(novo_pedido)
  session.commit()

  return {"mensagem":f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session=Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  """
  Cancela um pedido existente. 
    
  Apenas administradores ou o usuário do pedido possuem permissão para esta ação.
  """
  pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não encontrado")
  if not usuario.admin and usuario.id != pedido.usuario:
    raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
  pedido.status = "CANCELADO"
  session.commit()
  return{
    "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
    "pedido": pedido
  }

@order_router.get("/listar")
async def listar_pedidos(session: Session=Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  """
  Lista todos os pedidos de todos os usuários apenas Administradores tem acesso.
    
  Permite uma visão geral de todas as vendas e status dos pedidos no sistema.
  """
  if not usuario.admin:
    raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
  else:
    pedidos = session.query(Pedido).all()
    return {
      "pedidos": pedidos
      }
  
@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  """
  Adiciona pizza ao pedido e retorna um ID para futuras modificações.
     
  Recalcula automaticamente o valor total do pedido com base no preço unitário e quantidade.
  """
  pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não existente")
  if not usuario.admin and usuario.id != pedido.usuario:
    raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
  item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, item_pedido_schema.preco_unitario, id_pedido)
  session.add(item_pedido)
  pedido.calcular_preco()
  session.commit()
  return{
      "mensagem": "Item criado com sucesso",
      "item_id": item_pedido.id,
      "preco_pedido": pedido.preco
 }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  """
  Remove a pizza de um pedido.
  """
  item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
  pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()
  if not item_pedido:
    raise HTTPException(status_code=400, detail="Item no pedido não existente")
  if not usuario.admin and usuario.id != pedido.usuario:
    raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa operação")
  session.delete(item_pedido)
  pedido.calcular_preco()
  session.commit()
  return {
      "mensagem": "Item removido com sucesso",
      "quantidade_itens_pedido": len(pedido.itens),
      "pedido": pedido
  }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  """
  Altera o status do pedido para 'FINALIZADO'.
    
  Indica que o pedido foi concluído com sucesso.
  """
  pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não encontrado")
  if not usuario.admin and usuario.id != pedido.usuario:
    raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
  pedido.status = "FINALIZADO"
  session.commit()
  return {
      "mensagem": f"Pedido número: {pedido.id} finalizado com sucesso",
      "pedido": pedido
   }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  """
  Retorna os detalhes completos de um pedido específico.
    
  Exibe o status, valor total e a lista detalhada de itens incluídos.
  """
  pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
  if not pedido:
    raise HTTPException(status_code=400, detail="Pedido não encontrado")
  if not usuario.admin and usuario.id != pedido.usuario:
    raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
  return {
      "quantidade_itens_pedido": len(pedido.itens),
      "pedido": pedido
  }

@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
  """
  Recupera o histórico de pedidos do usuário autenticado.
    
  Utiliza o token JWT para identificar o usuário e retornar apenas os seus pedidos.
  """
  pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()
  return pedidos
