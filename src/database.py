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
                valor_centavos INTEGER NOT NULL CHECK(valor_centavos >= 0),
                data TEXT NOT NULL,
                categoria TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Migração automática da V1 inicial (valor REAL) para valor_centavos INTEGER.
        colunas = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(lancamentos)").fetchall()
        }
        if "valor" in colunas and "valor_centavos" not in colunas:
            conn.executescript(
                """
                BEGIN;
                CREATE TABLE lancamentos_novo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                    descricao TEXT NOT NULL,
                    valor_centavos INTEGER NOT NULL CHECK(valor_centavos >= 0),
                    data TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                INSERT INTO lancamentos_novo (id, tipo, descricao, valor_centavos, data, categoria, criado_em)
                SELECT
                    id,
                    tipo,
                    descricao,
                    CAST(ROUND(valor * 100) AS INTEGER),
                    data,
                    categoria,
                    criado_em
                FROM lancamentos;

                DROP TABLE lancamentos;
                ALTER TABLE lancamentos_novo RENAME TO lancamentos;
                COMMIT;
                """
            )
        conn.commit()
