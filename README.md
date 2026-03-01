# CAAR-Agente-musingdoc

Agente IA conversacional da **Musing Doc** — atende visitantes via chat no site e WhatsApp, conhece profundamente todos os serviços, produtos e preços da plataforma, e guia potenciais clientes até a conversão.

## Stack

- **Python 3.11+** / **FastAPI** — API REST
- **LangChain + Claude API** (Anthropic) — orquestração e modelo de linguagem
- **Redis** — memória de conversa por sessão
- **Docker** — deploy containerizado

## Setup local

```bash
# 1. Clone o repositório
git clone https://github.com/carlosars2/CAAR-Agente-musingdoc.git
cd CAAR-Agente-musingdoc

# 2. Copie e configure as variáveis de ambiente
cp .env.example .env
# Edite .env com sua ANTHROPIC_API_KEY

# 3. Suba com Docker Compose
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.

## Endpoints

| Método | Rota                     | Descrição                    |
|--------|--------------------------|------------------------------|
| POST   | `/api/chat`              | Envia mensagem ao agente     |
| GET    | `/api/webhook/whatsapp`  | Verificação webhook WhatsApp |
| POST   | `/api/webhook/whatsapp`  | Recebe mensagens WhatsApp    |
| GET    | `/health`                | Health check                 |

### Exemplo de uso

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "message": "Olá, quero saber sobre os agentes de IA"}'
```

## Testes

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Deploy (VPS)

```bash
# Na VPS, com Docker instalado:
docker compose up -d --build

# Configurar nginx como proxy reverso para porta 8000
```
