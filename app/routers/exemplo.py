# meu_projeto/app/routers/exemplo.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/exemplo")
def get_exemplo():
    return {"mensagem": "Rota de exemplo"}
