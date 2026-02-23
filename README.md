# Sistema Financeiro (v1 + BI)

Projeto em Python com:
- controle financeiro via terminal (CLI)
- módulo web de Business Intelligence para importação e analytics da 99Food

## Estrutura

```text
sistema-financeiro/
├── data/                     # banco SQLite e uploads
├── src/
│   ├── bi/
│   │   └── service.py        # serviços de BI (importação + dashboard)
│   ├── static/
│   │   └── styles.css        # design system base
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   └── bi_99food.html
│   ├── database.py           # conexão e criação das tabelas
│   ├── finance.py            # regras de negócio de lançamentos
│   ├── main.py               # interface de terminal (CLI)
│   └── webapp.py             # backend web (rotas /bi/99food)
├── requirements.txt
└── README.md
```

## Funcionalidades

### Financeiro (CLI)
- Adição de lançamentos de **entrada** e **saída**.
- Listagem de lançamentos.
- Cálculo de saldo total (**entradas - saídas**).

### BI 99Food (Web)
- Tela `/bi/99food` com upload de múltiplos arquivos Excel.
- Suporte para:
  - relatório de pedidos
  - relatório de itens
- Processamento com `pandas`.
- Relacionamento por `ID do pedido`.
- Persistência analítica nas tabelas:
  - `bi_99food_pedidos`
  - `bi_99food_itens`
- Dashboard com:
  - KPIs (faturamento total, pedidos, ticket médio, itens vendidos)
  - séries (faturamento por dia, pedidos por hora, vendas por dia da semana)
  - rankings por faturamento e quantidade
  - filtros por período e produto

## Rotas backend

- `POST /bi/99food/upload`
- `GET /bi/99food/dashboard`
- `GET /bi/99food` (tela)

## Arquitetura preparada para novos provedores

Estrutura de serviço já prevê extensão para:
- `/bi/ifood`
- `/bi/keeta`

## Como executar

### 1) Instalar dependências

```bash
pip install -r requirements.txt
```

### 2) Executar CLI

```bash
python src/main.py
```

### 3) Executar Web

```bash
python src/webapp.py
```

Abra no navegador:
- `http://localhost:5000/`
- `http://localhost:5000/bi/99food`
