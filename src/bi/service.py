"""Serviços de BI para importação e analytics de marketplaces."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from database import DATA_DIR, get_connection


@dataclass(frozen=True)
class BIProvider:
    """Representa um provedor de marketplace para BI."""

    slug: str
    nome: str


PROVEDOR_99FOOD = BIProvider(slug="99food", nome="99Food")
PROVEDORES_FUTUROS = [BIProvider(slug="ifood", nome="iFood"), BIProvider(slug="keeta", nome="Keeta")]

UPLOAD_DIR = DATA_DIR / "uploads" / "bi"


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    colunas = [str(col).strip().lower() for col in df.columns]
    return df.rename(columns={antiga: nova for antiga, nova in zip(df.columns, colunas, strict=False)})


def _identificar_tipo_relatorio(df: pd.DataFrame) -> str:
    colunas = set(df.columns)
    if {"id do pedido", "status"}.issubset(colunas):
        return "pedidos"
    if {"id do pedido", "nome do item", "quantidade vendida"}.issubset(colunas):
        return "itens"
    raise ValueError("Arquivo não reconhecido. Use relatório de pedidos ou itens da 99Food.")


def _parse_datetime(valor: Any) -> str:
    if pd.isna(valor):
        raise ValueError("Data/hora do pedido está vazia.")
    if isinstance(valor, datetime):
        return valor.isoformat(sep=" ", timespec="seconds")
    convertido = pd.to_datetime(valor, errors="coerce")
    if pd.isna(convertido):
        raise ValueError(f"Data/hora inválida: {valor}")
    return convertido.to_pydatetime().isoformat(sep=" ", timespec="seconds")


def _ler_excel(caminho: Path) -> pd.DataFrame:
    df = pd.read_excel(caminho)
    df = _normalizar_colunas(df)
    if "id do pedido" not in df.columns:
        raise ValueError("O arquivo precisa conter a coluna 'ID do pedido'.")
    return df


def _salvar_relatorio_pedidos(df: pd.DataFrame, arquivo_origem: str) -> int:
    linhas = 0
    with get_connection() as conn:
        for _, row in df.iterrows():
            pedido_id = str(row.get("id do pedido", "")).strip()
            if not pedido_id:
                continue
            conn.execute(
                """
                INSERT INTO bi_99food_pedidos (
                    pedido_id,
                    data_hora_pedido,
                    status,
                    tempo_preparo_min,
                    tempo_entrega_min,
                    arquivo_origem
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(pedido_id) DO UPDATE SET
                    data_hora_pedido = excluded.data_hora_pedido,
                    status = excluded.status,
                    tempo_preparo_min = excluded.tempo_preparo_min,
                    tempo_entrega_min = excluded.tempo_entrega_min,
                    arquivo_origem = excluded.arquivo_origem,
                    atualizado_em = CURRENT_TIMESTAMP
                """,
                (
                    pedido_id,
                    _parse_datetime(row.get("data e hora do pedido")),
                    str(row.get("status", "")).strip(),
                    float(row.get("tempo preparo", 0) or 0),
                    float(row.get("tempo entrega", 0) or 0),
                    arquivo_origem,
                ),
            )
            linhas += 1
        conn.commit()
    return linhas


def _salvar_relatorio_itens(df: pd.DataFrame, arquivo_origem: str) -> int:
    linhas = 0
    with get_connection() as conn:
        for _, row in df.iterrows():
            pedido_id = str(row.get("id do pedido", "")).strip()
            nome_item = str(row.get("nome do item", "")).strip()
            if not pedido_id or not nome_item:
                continue
            quantidade = float(row.get("quantidade vendida", 0) or 0)
            receita = float(row.get("receita do item", 0) or 0)
            preco_medio = float(row.get("preço médio", 0) or 0)
            conn.execute(
                """
                INSERT INTO bi_99food_itens (
                    pedido_id,
                    nome_item,
                    quantidade_vendida,
                    receita_item,
                    preco_medio,
                    arquivo_origem
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (pedido_id, nome_item, quantidade, receita, preco_medio, arquivo_origem),
            )
            linhas += 1
        conn.commit()
    return linhas


def importar_arquivos_99food(arquivos: list[tuple[str, bytes]]) -> dict[str, Any]:
    """Importa múltiplos arquivos Excel da 99Food e salva no banco."""
    if not arquivos:
        raise ValueError("Nenhum arquivo foi enviado.")

    destino = UPLOAD_DIR / PROVEDOR_99FOOD.slug
    destino.mkdir(parents=True, exist_ok=True)

    resultado = {"pedidos": 0, "itens": 0, "arquivos": []}

    for nome_arquivo, conteudo in arquivos:
        caminho = destino / nome_arquivo
        caminho.write_bytes(conteudo)

        df = _ler_excel(caminho)
        tipo = _identificar_tipo_relatorio(df)
        if tipo == "pedidos":
            processadas = _salvar_relatorio_pedidos(df, nome_arquivo)
        else:
            processadas = _salvar_relatorio_itens(df, nome_arquivo)

        resultado[tipo] += processadas
        resultado["arquivos"].append({"nome": nome_arquivo, "tipo": tipo, "linhas": processadas})

    return resultado


def carregar_dashboard_99food(data_inicial: str | None = None, data_final: str | None = None, produto: str | None = None) -> dict[str, Any]:
    """Retorna KPIs e séries para dashboard analítico da 99Food."""
    filtros: list[str] = ["1=1"]
    parametros: list[Any] = []

    if data_inicial:
        filtros.append("date(p.data_hora_pedido) >= date(?)")
        parametros.append(data_inicial)
    if data_final:
        filtros.append("date(p.data_hora_pedido) <= date(?)")
        parametros.append(data_final)
    if produto:
        filtros.append("i.nome_item = ?")
        parametros.append(produto)

    where = " AND ".join(filtros)

    with get_connection() as conn:
        kpis = conn.execute(
            f"""
            SELECT
                COALESCE(SUM(i.receita_item), 0) AS faturamento_total,
                COUNT(DISTINCT p.pedido_id) AS total_pedidos,
                COALESCE(SUM(i.quantidade_vendida), 0) AS total_itens_vendidos,
                CASE
                    WHEN COUNT(DISTINCT p.pedido_id) = 0 THEN 0
                    ELSE COALESCE(SUM(i.receita_item), 0) / COUNT(DISTINCT p.pedido_id)
                END AS ticket_medio
            FROM bi_99food_pedidos p
            LEFT JOIN bi_99food_itens i ON i.pedido_id = p.pedido_id
            WHERE {where}
            """,
            parametros,
        ).fetchone()

        faturamento_por_dia = conn.execute(
            f"""
            SELECT date(p.data_hora_pedido) AS dia, COALESCE(SUM(i.receita_item), 0) AS valor
            FROM bi_99food_pedidos p
            LEFT JOIN bi_99food_itens i ON i.pedido_id = p.pedido_id
            WHERE {where}
            GROUP BY date(p.data_hora_pedido)
            ORDER BY dia
            """,
            parametros,
        ).fetchall()

        pedidos_por_hora = conn.execute(
            f"""
            SELECT strftime('%H', p.data_hora_pedido) AS hora, COUNT(DISTINCT p.pedido_id) AS pedidos
            FROM bi_99food_pedidos p
            LEFT JOIN bi_99food_itens i ON i.pedido_id = p.pedido_id
            WHERE {where}
            GROUP BY strftime('%H', p.data_hora_pedido)
            ORDER BY hora
            """,
            parametros,
        ).fetchall()

        vendas_semana = conn.execute(
            f"""
            SELECT
                CASE cast(strftime('%w', p.data_hora_pedido) as integer)
                    WHEN 0 THEN 'Domingo'
                    WHEN 1 THEN 'Segunda'
                    WHEN 2 THEN 'Terça'
                    WHEN 3 THEN 'Quarta'
                    WHEN 4 THEN 'Quinta'
                    WHEN 5 THEN 'Sexta'
                    ELSE 'Sábado'
                END AS dia_semana,
                COALESCE(SUM(i.receita_item), 0) AS valor
            FROM bi_99food_pedidos p
            LEFT JOIN bi_99food_itens i ON i.pedido_id = p.pedido_id
            WHERE {where}
            GROUP BY strftime('%w', p.data_hora_pedido)
            ORDER BY cast(strftime('%w', p.data_hora_pedido) as integer)
            """,
            parametros,
        ).fetchall()

        ranking_faturamento = conn.execute(
            f"""
            SELECT i.nome_item, COALESCE(SUM(i.receita_item), 0) AS valor
            FROM bi_99food_pedidos p
            JOIN bi_99food_itens i ON i.pedido_id = p.pedido_id
            WHERE {where}
            GROUP BY i.nome_item
            ORDER BY valor DESC
            LIMIT 10
            """,
            parametros,
        ).fetchall()

        ranking_quantidade = conn.execute(
            f"""
            SELECT i.nome_item, COALESCE(SUM(i.quantidade_vendida), 0) AS quantidade
            FROM bi_99food_pedidos p
            JOIN bi_99food_itens i ON i.pedido_id = p.pedido_id
            WHERE {where}
            GROUP BY i.nome_item
            ORDER BY quantidade DESC
            LIMIT 10
            """,
            parametros,
        ).fetchall()

        produtos = conn.execute(
            """
            SELECT DISTINCT nome_item
            FROM bi_99food_itens
            ORDER BY nome_item
            """
        ).fetchall()

    return {
        "kpis": dict(kpis),
        "graficos": {
            "faturamento_por_dia": [dict(item) for item in faturamento_por_dia],
            "pedidos_por_hora": [dict(item) for item in pedidos_por_hora],
            "vendas_por_dia_semana": [dict(item) for item in vendas_semana],
        },
        "produtos": {
            "ranking_faturamento": [dict(item) for item in ranking_faturamento],
            "ranking_quantidade": [dict(item) for item in ranking_quantidade],
            "filtro": [item[0] for item in produtos],
        },
        "provedores_futuros": [p.__dict__ for p in PROVEDORES_FUTUROS],
    }
