"""Interface de terminal (CLI) do sistema financeiro."""

from __future__ import annotations

from database import init_db
from finance import adicionar_lancamento, calcular_saldo, listar_lancamentos


def exibir_menu() -> None:
    """Mostra o menu principal."""
    print("\n=== Sistema Financeiro (v1) ===")
    print("1 - Adicionar entrada")
    print("2 - Adicionar saída")
    print("3 - Listar lançamentos")
    print("4 - Ver saldo")
    print("0 - Sair")


def ler_valor() -> float:
    """Lê e valida valor numérico informado pelo usuário."""
    while True:
        bruto = input("Valor: R$ ").replace(",", ".").strip()
        try:
            valor = float(bruto)
            if valor < 0:
                print("O valor não pode ser negativo.")
                continue
            return valor
        except ValueError:
            print("Valor inválido. Digite um número, ex: 120.50")


def coletar_dados_lancamento(tipo: str) -> None:
    """Coleta dados e cria lançamento."""
    print(f"\nNovo lançamento ({tipo})")
    descricao = input("Descrição: ").strip()
    valor = ler_valor()
    data = input("Data (YYYY-MM-DD): ").strip()
    categoria = input("Categoria: ").strip()

    lancamento_id = adicionar_lancamento(tipo, descricao, valor, data, categoria)
    print(f"Lançamento salvo com sucesso! ID: {lancamento_id}")


def mostrar_lancamentos() -> None:
    """Exibe os lançamentos no terminal."""
    itens = listar_lancamentos()
    if not itens:
        print("\nNenhum lançamento cadastrado.")
        return

    print("\n=== Lançamentos ===")
    for item in itens:
        sinal = "+" if item["tipo"] == "entrada" else "-"
        print(
            f"#{item['id']} | {item['data']} | {item['categoria']} | "
            f"{item['descricao']} | {sinal}R$ {item['valor']:.2f}"
        )


def mostrar_saldo() -> None:
    """Mostra o saldo total consolidado."""
    saldo = calcular_saldo()
    print(f"\nSaldo atual: R$ {saldo:.2f}")


def main() -> None:
    """Ponto de entrada da aplicação CLI."""
    # Inicializa o banco automaticamente ao abrir o sistema
    init_db()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                coletar_dados_lancamento("entrada")
            elif opcao == "2":
                coletar_dados_lancamento("saida")
            elif opcao == "3":
                mostrar_lancamentos()
            elif opcao == "4":
                mostrar_saldo()
            elif opcao == "0":
                print("Até mais!")
                break
            else:
                print("Opção inválida. Tente novamente.")
        except Exception as exc:  # Tratamento simples para manter a CLI didática
            print(f"Erro ao processar operação: {exc}")


if __name__ == "__main__":
    main()
