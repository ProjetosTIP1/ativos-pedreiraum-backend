# Valemix Assets - Backend

Este é o backend do sistema **Valemix Assets**, um catálogo robusto para gerenciamento e exibição de ativos industriais e pesados. O projeto foi desenvolvido seguindo rigorosos padrões de engenharia de software, priorizando a maturidade do sistema, a manutenibilidade e a performance.

## 🏗️ Arquitetura e Filosofia

O sistema foi construído sobre os pilares da **Clean Architecture** (Arquitetura Limpa) e princípios **SOLID**, garantindo que as regras de negócio sejam independentes de frameworks, bancos de dados ou qualquer agente externo.

### Camadas do Projeto:
- **Domain:** Contém as entidades principais, enums (Value Objects) e as interfaces (Abstrações) dos repositórios. É o coração do sistema e não possui dependências externas.
- **Application:** Implementa os casos de uso e serviços da aplicação, orquestrando o fluxo de dados entre o domínio e o mundo externo.
- **Infrastructure:** Responsável pelas implementações concretas (Persistência com PostgreSQL, serviços de terceiros, loggers).
- **API:** Camada de entrada (Controllers) que expõe os endpoints via FastAPI.
- **Core:** Configurações globais, segurança e helpers compartilhados.

### 🚫 Mandato No-ORM (Repository Pattern)
Seguindo a filosofia de que "o código é um passivo", optamos por **não utilizar ORMs pesados**. Toda a persistência é feita através de consultas SQL puras utilizando o driver assíncrono `asyncpg`. 
- **Por que?** Maior performance, controle total sobre os planos de execução do banco de dados e prevenção de problemas comuns como `N+1`.
- **Implementação:** Utilizamos o padrão *Repository* para isolar o SQL puro da lógica de negócio.

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3.12+
- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) (Assíncrono e de alta performance)
- **Validação:** [Pydantic v2](https://docs.pydantic.dev/) para contratos de dados rigorosos em todas as fronteiras.
- **Banco de Dados:** PostgreSQL com I/O não bloqueante via `asyncpg`.
- **Autenticação:** JWT (JSON Web Tokens) com `python-jose`.
- **Segurança:** `bcrypt` para hashing de senhas.
- **Gerenciador de Dependências:** [uv](https://github.com/astral-sh/uv) (Extremamente rápido).

## 🚀 Principais Funcionalidades

- **Gestão de Imagens Local:** Upload e serviço de arquivos estáticos otimizado, sem dependências de serviços externos para armazenamento básico.
- **Busca Avançada:** Filtros complexos por marca, ano, categoria e status, utilizando o potencial do PostgreSQL.
- **Dashboard Administrativo:** Endpoints protegidos para gestão completa do catálogo e visualização de estatísticas.

## ⚙️ Configuração e Execução

### Pré-requisitos
- Python 3.12+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) (Recomendado) ou `pip`

### Configuração do Ambiente
1. Clone o repositório.
2. Crie um arquivo `.env` baseado no `.sample.env`:
   ```bash
   cp .sample.env .env
   ```
3. Ajuste as credenciais do banco de dados e as chaves de segurança no `.env`.

### Rodando a Aplicação
Instale as dependências e inicie o servidor:

```bash
# Com uv
uv sync
uv run python main.py

# Ou com pip
pip install -r requirements.txt
python main.py
```

O servidor estará disponível em `http://localhost:8000`. A documentação interativa da API (Swagger) pode ser acessada em `http://localhost:8000/docs`.

---
*Este projeto é mantido seguindo a filosofia de que o melhor código é aquele que pode ser facilmente compreendido e testado.*
