"""Camada de regras de negócio para lançamentos financeiros."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from database import get_connection


CENTAVOS = Decimal("100")


def _valor_para_centavos(valor: float) -> int:
    """Converte valor monetário para inteiro em centavos."""
    valor_decimal = Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(valor_decimal * CENTAVOS)


def _centavos_para_valor(valor_centavos: int) -> float:
    """Converte inteiro em centavos para decimal em reais."""
    return float(Decimal(valor_centavos) / CENTAVOS)


def adicionar_lancamento(
    tipo: str,
    descricao: str,
    valor: float,
    data: str,
    categoria: str,
) -> int:
    """Adiciona um lançamento e retorna o ID criado."""
    tipo_normalizado = tipo.strip().lower()
    if tipo_normalizado not in ("entrada", "saida"):
        raise ValueError("Tipo inválido. Use 'entrada' ou 'saida'.")

    if valor < 0:
        raise ValueError("Valor não pode ser negativo.")

    valor_centavos = _valor_para_centavos(valor)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO lancamentos (tipo, descricao, valor_centavos, data, categoria)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tipo_normalizado, descricao.strip(), valor_centavos, data.strip(), categoria.strip()),
        )
        conn.commit()
        return int(cursor.lastrowid)


def listar_lancamentos() -> list[dict[str, Any]]:
    """Lista todos os lançamentos em ordem de data (mais recentes primeiro)."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, tipo, descricao, valor_centavos, data, categoria, criado_em
            FROM lancamentos
            ORDER BY data DESC, id DESC
            """
        ).fetchall()

    return [
        {
            **dict(row),
            "valor": _centavos_para_valor(int(row["valor_centavos"])),
        }
        for row in rows
    ]


def calcular_saldo() -> float:
    """Calcula saldo total: soma(entradas) - soma(saídas)."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor_centavos ELSE 0 END), 0) AS total_entradas_centavos,
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor_centavos ELSE 0 END), 0) AS total_saidas_centavos
            FROM lancamentos
            """
        ).fetchone()

    total_entradas_centavos = int(row["total_entradas_centavos"])
    total_saidas_centavos = int(row["total_saidas_centavos"])
    saldo_centavos = total_entradas_centavos - total_saidas_centavos
    return _centavos_para_valor(saldo_centavos)


def listar_por_periodo(data_inicial: str, data_final: str) -> list[dict[str, Any]]:
    """Lista lançamentos entre duas datas (inclusive).

    Espera datas no formato ISO simples: YYYY-MM-DD.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, tipo, descricao, valor_centavos, data, categoria, criado_em
            FROM lancamentos
            WHERE data BETWEEN ? AND ?
            ORDER BY data ASC, id ASC
            """,
            (data_inicial.strip(), data_final.strip()),
        ).fetchall()

    return [
        {
            **dict(row),
            "valor": _centavos_para_valor(int(row["valor_centavos"])),
        }
        for row in rows
    ]


def importar_nfe_xml(caminho_xml: str) -> dict[str, Any]:
    """Função preparada para futura importação de XML de NF-e.

    Esta função foi criada como ponto de extensão para a versão futura.
    Ideia de evolução:
    - Ler XML da NF-e
    - Extrair itens/valores relevantes
    - Converter em lançamentos automáticos
    - Salvar no banco
    """
    # Nesta V1, retornamos um resultado didático indicando que ainda não foi implementado.
    return {
        "status": "nao_implementado",
        "mensagem": "Importação de XML de NF-e será implementada em versão futura.",
        "arquivo": caminho_xml,
    }
