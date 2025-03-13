"""
Objetos do sqlalchemy core para a realização da conexão e operação do Banco de Dados
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_CONNECTION = URL.create(
    drivername="postgresql",
    username="tecsci",
    password="SiZ+e+2CWL",
    host="54.165.71.198",
    port=32046,
    database="tracker"
)
class Base(DeclarativeBase):
    pass
engine = create_engine(DB_CONNECTION, echo=False)
SessionLocal = sessionmaker(bind=engine)