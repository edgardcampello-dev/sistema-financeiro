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
            CREATE TABLE IF NOT EXISTS bi_99food_pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id TEXT NOT NULL UNIQUE,
                data_hora_pedido TEXT NOT NULL,
                status TEXT NOT NULL,
                tempo_preparo_min REAL NOT NULL DEFAULT 0,
                tempo_entrega_min REAL NOT NULL DEFAULT 0,
                arquivo_origem TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bi_99food_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id TEXT NOT NULL,
                nome_item TEXT NOT NULL,
                quantidade_vendida REAL NOT NULL DEFAULT 0,
                receita_item REAL NOT NULL DEFAULT 0,
                preco_medio REAL NOT NULL DEFAULT 0,
                arquivo_origem TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pedido_id) REFERENCES bi_99food_pedidos(pedido_id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bi_99food_pedidos_data_hora
            ON bi_99food_pedidos(data_hora_pedido)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bi_99food_itens_pedido_id
            ON bi_99food_itens(pedido_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bi_99food_itens_nome_item
            ON bi_99food_itens(nome_item)
            """
        )
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
