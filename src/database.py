"""Camada de persistência do sistema financeiro.

Este módulo centraliza:
- Caminho do banco SQLite em /data
- Conexão com o banco
- Criação automática das tabelas
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

# Diretórios do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "financeiro.db"


def get_connection() -> sqlite3.Connection:
    """Retorna conexão SQLite com acesso por nome de coluna."""
    # Garante que a pasta /data exista antes de abrir o arquivo .db
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Inicializa o banco de dados e cria tabelas se não existirem."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                descricao TEXT NOT NULL,
                valor REAL NOT NULL CHECK(valor >= 0),
                data TEXT NOT NULL,
                categoria TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
