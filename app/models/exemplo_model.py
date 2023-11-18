# meu_projeto/app/models/exemplo_model.py

from pydantic import BaseModel

class ExemploModel(BaseModel):
    nome: str
    idade: int
