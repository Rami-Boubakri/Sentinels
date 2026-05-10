# 🛡️ SENTINELS — AI-Powered Multi-Agent NPL Management System

> An enterprise-grade, real-time multi-agent AI platform built for STB Bank Tunisia to detect, analyze, and orchestrate responses to Non-Performing Loan (NPL) risks across banking departments.

---

## 📌 Overview

SENTINELS is a full-stack agentic AI system that ingests banking events (early warning signals, loan restructuring requests, regulatory inquiries, etc.), routes them through a security layer, and dispatches specialized department agents in parallel to produce structured risk analyses — all streamed live to the operator via Server-Sent Events (SSE).

Built as a proof-of-concept for STB Bank's NPL governance pipeline, it demonstrates how LLM-powered agents can augment human decision-making in credit risk management.

---

## 🏗️ Architecture

```
Input Event (Operator / API)
        │
        ▼
┌─────────────────────┐
│   Security Layer    │  ← Prompt injection scan, input validation,
│                     │    rate limiting, sanitization
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    Orchestrator     │  ← Routes event to relevant departments
│  (Routing Matrix)   │    based on event type + context
└────────┬────────────┘
         │
    ┌────┴─────────────────────────┐
    ▼          ▼          ▼        ▼
 DIR_RISQUE  DIR_SFAX  DIR_GGEI  DIR_ALM  ...6 agents total
    │          │          │        │
    └──────────┴──────────┴────────┘
                    │
                    ▼
         Structured JSON Reports
                    │
                    ▼
         Live SSE Stream → Frontend Dashboard
```

---

## ⚙️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Database | SQLite (SQLAlchemy ORM) |
| LLM Provider | Groq API (`llama-3.3-70b-versatile`) |
| Streaming | Server-Sent Events (SSE) |
| Security | Custom prompt injection detection (40+ patterns) |
| Auth | JWT (python-jose) |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS |
| Language | TypeScript |
| Real-time | EventSource API (SSE client) |

---

## 🤖 Agents

| Agent | Department | Responsibility |
|---|---|---|
| `surveillance_risque_credit.py` | DIR_RISQUE | Credit risk scoring, DPD analysis, provisioning recommendation |
| `regionale_sfax.py` | DIR_SFAX | Regional branch context, borrower relationship assessment |
| `analyse_credit_ggei.py` | DIR_GGEI | Large corporate & SME portfolio analysis |
| `donnees_analytiques.py` | DIR_DATA | Data analytics, trend detection, financial ratios |
| `garanties.py` | DIR_GARANTIES | Collateral and guarantee valuation |
| `controle_gestion_alm.py` | DIR_ALM | Asset-liability management, liquidity impact |

Each agent receives the sanitized event, runs an LLM completion via Groq, and returns a structured JSON report with: `analysis`, `proposed_action`, `confidence`, and `risk_level`.

---

## 🔐 Security Layer

- **Prompt Injection Detection** — 40+ regex patterns across 7 attack tiers (direct override, persona hijacking, delimiter injection, privilege escalation, base64-encoded attacks, unicode homoglyph bypasses)
- **Input Validation** — field type/length checks, event_type allowlist, suspicious character blocklist
- **Sanitization** — HTML/script stripping, unicode normalization, LLM-safe truncation
- **Rate Limiting** — per-IP sliding window (10 req/min default), burst protection

---

## 🗂️ Project Structure

```
Sentinels2/
├── backend/
│   └── app/
│       ├── agents/          # 6 department LLM agents + base class
│       ├── api/v1/          # FastAPI routes (inputs, tickets, reports, stream, audit)
│       ├── core/            # Auth, audit logging
│       ├── models/          # SQLAlchemy models
│       ├── orchestrator/    # Event routing + pipeline orchestration
│       ├── schemas/         # Pydantic schemas
│       ├── security_layer/  # Injection detection, validation, rate limiting
│       ├── config.py        # Settings (pydantic-settings)
│       ├── database.py      # DB session management
│       └── main.py          # FastAPI app entry point
├── frontend/
│   └── src/app/
│       ├── (dashboard)/     # Dashboard, tickets, audit log pages
│       ├── submit/          # Event submission form
│       └── components/      # Shared UI components
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/Rami-Boubakri/sentinels.git
cd sentinels
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create your `.env` file:
```env
GROQ_API_KEY=your_groq_key_here
DATABASE_URL=sqlite:///./sentinels.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run the backend:
```bash
cd app
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 📸 Screenshots

> Dashboard → Submit Event → Live Pipeline → Department Reports

*Add screenshots here after deployment*

---

## 📄 License

MIT — built for educational and research purposes.

---

## 👤 Author

**Rami Boubakri** — [GitHub](https://github.com/Rami-Boubakri)

> Built with FastAPI, Next.js, and Groq LLM. Inspired by real NPL governance challenges in Tunisian banking.
