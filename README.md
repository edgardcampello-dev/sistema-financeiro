# Sistema Financeiro (v1)

Projeto simples e didático em Python para controle financeiro via terminal (CLI).

## Estrutura

```text
sistema-financeiro/
├── data/                # banco SQLite (criado automaticamente)
├── src/
│   ├── database.py      # conexão e criação das tabelas
│   ├── finance.py       # regras de negócio
│   └── main.py          # interface de terminal (CLI)
├── requirements.txt
└── README.md
```

## Funcionalidades

- Inicialização automática do banco de dados SQLite em arquivo dentro de `/data`.
- Adição de lançamentos de **entrada** e **saída**.
- Listagem de lançamentos.
- Cálculo de saldo total (**entradas - saídas**).
- Funções extras:
  - `calcular_saldo()`
  - `listar_por_periodo(data_inicial, data_final)`
- Função preparada para futura integração com XML de NF-e:
  - `importar_nfe_xml(caminho_xml)`

## Tabela criada

Tabela: `lancamentos`

Campos:
- `id` (integer, primary key, autoincrement)
- `tipo` (`entrada` ou `saida`)
- `descricao` (texto)
- `valor` (real)
- `data` (texto)
- `categoria` (texto)
- `criado_em` (timestamp)

## Como executar

### 1) Criar e ativar ambiente virtual (opcional, recomendado)

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 3) Executar a aplicação

```bash
python src/main.py
```

## Menu da aplicação

- `1` - Adicionar entrada
- `2` - Adicionar saída
- `3` - Listar lançamentos
- `4` - Ver saldo
- `0` - Sair

## Observações

- O campo `data` está em formato de texto (sugestão: `YYYY-MM-DD`) para simplificar a V1.
- A função de importação de XML NF-e foi deixada como ponto de extensão para versões futuras.
