# AI-Powered ITSM Helpdesk Automation Platform

An enterprise SaaS platform integrating **Supabase (PostgreSQL, Auth, RLS)**, **Pinecone (Vector DB)**, **Groq API (GPT-OSS Models)**, and **ServiceNow REST API** to automate helpdesk operations, document retrieval, guided self-healing diagnostics, and software provisioning.

---

## 1. Architecture Overview

```
itsm-helpdesk/
├── src/                          # React + Vite Enterprise Frontend
│   ├── App.jsx                   # Main SaaS Interface (Self-Service + Admin Portals)
│   ├── main.jsx                  # React DOM Entry
│   └── index.css                 # Enterprise Design System
├── backend/
│   ├── app.py                    # Flask REST API Server
│   ├── config.py                 # Environment & Integration Config
│   ├── requirements.txt          # Python Dependencies
│   ├── ai/
│   │   ├── groq_client.py        # Groq GPT-OSS API Client
│   │   ├── ticket_classifier.py  # AI Ticket Intake & Schema Validator
│   │   ├── rag_pipeline.py       # Pinecone + 384-dim Embedding RAG
│   │   └── agent_orchestrator.py # Multi-Intent Chat Orchestrator
│   ├── automation/
│   │   ├── tool_registry.py      # Approved Diagnostic Tools with RBAC
│   │   └── workflows.py          # Bounded State Machine Self-Heal Workflows
│   ├── integrations/
│   │   └── servicenow.py         # ServiceNow REST Table API & Demo Mode
│   ├── models/
│   │   └── schemas.py            # Pydantic Schemas
│   ├── repositories/
│   │   ├── supabase_client.py    # Supabase Client Provider
│   │   └── db_repository.py      # Unified Data Access Layer
│   ├── routes/                   # REST API Blueprints
│   └── tests/                    # Automated Test Suites
├── supabase/
│   └── migrations/
│       ├── 20261018000001_init_itsm_schema.sql  # Full Table Schema & RLS
│       └── 20261018000002_seed_data.sql         # Seed Software Catalog & Runbooks
├── .env.example                  # Environment Template
└── README.md
```

---

## 2. Mandatory Core Capabilities

1. **Intelligent Ticket Intake**:
   - Natural language problem extraction via Groq GPT-OSS.
   - Structured JSON validation: Title, Description, Category, Impact, Urgency, Symptoms, Affected Service.
   - Deterministic ITIL 4x4 Priority Matrix calculation.
   - User-editable preview before saving to Supabase and syncing to ServiceNow.

2. **Self-Service Portal & AI Chatbot (RAG)**:
   - Grounded question answering using **Pinecone** and 384-dimensional embeddings (`sentence-transformers/all-MiniLM-L6-v2`).
   - Clickable source citations (`[Document Title, Section]`).
   - Zero-hallucination policy guardrails. If no internal documentation exists, offers immediate ticket creation.

3. **Auto-Resolution & Self-Healing Workflows**:
   - 3 approved diagnostic workflows:
     - **Network Troubleshooting**: DNS resolution probes and VPN gateway reachability.
     - **Disk Space Guidance**: Storage utilization, safe temporary cache identification.
     - **Application Troubleshooting**: Process lock analysis and corrupt cache reset.
   - Truthful execution mode labeling: `real`, `guided`, `simulated`.
   - Verification state machine with automatic ticket escalation if unresolved.

4. **Software Provisioning Automation**:
   - Software Catalogue with automated policy enforcement:
     - **Pre-Approved**: Instant silent deployment (e.g. Visual Studio Code, Python 3.12).
     - **Approval Required**: IT Managerial review queue (e.g. Docker Desktop, ERP Access).
   - Real, simulated, and manual execution tracking.

5. **External ServiceNow Integration**:
   - Dedicated ServiceNow REST API client using Table API (`/api/now/table/incident`).
   - Incident creation, field mapping (Impact/Urgency 1-3), status synchronization.
   - Resilient design: If ServiceNow is temporarily unreachable, internal Supabase tickets remain intact.
   - Full **Demo Mode** with clearly identifiable simulated references (`DEMO-INC-XXXX`).

---

## 3. ITIL Priority Matrix (4x4 Deterministic Engine)

Priority is calculated by the backend engine rather than unconstrained LLM generation:

| Impact \ Urgency | Critical | High | Medium | Low |
| :--- | :--- | :--- | :--- | :--- |
| **Critical** | Critical | Critical | High | Medium |
| **High** | Critical | High | Medium | Low |
| **Medium** | High | Medium | Medium | Low |
| **Low** | Medium | Low | Low | Low |

---

## 4. Setup and Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### Backend Setup
1. Open a terminal in `backend/`:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Start the Flask server:
   ```bash
   python app.py
   ```
   *The backend starts at `https://itsm-lqs3.vercel.app`.*

### Frontend Setup
1. In the root workspace:
   ```bash
   npm run dev
   ```
   *The frontend starts at `http://localhost:5173`.*

---

## 5. Environment Variables Configuration

See `.env.example` for all configuration variables:

```env
# Backend
FLASK_ENV=development
PORT=5000
FRONTEND_ORIGIN=http://localhost:5173

# Supabase (Database & Auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Groq API (GPT-OSS Models)
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_FALLBACK_MODEL=openai/gpt-oss-20b

# Pinecone (Vector Database)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=itsm-knowledge
PINECONE_NAMESPACE=itsm-public
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ServiceNow REST API
SERVICENOW_INSTANCE_URL=https://devXXXXX.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your-password
SERVICENOW_AUTH_MODE=basic
SERVICENOW_DEMO_MODE=true
```

---

## 6. End-to-End Demonstration Scenarios

- **Scenario A (Intelligent Intake)**: Enter `"My laptop is connected to Wi-Fi, but I cannot access the internet. I have an important meeting soon."` Click *Analyze & Triage Problem*. Review the calculated High Priority preview and click *Confirm & Submit Ticket*.
- **Scenario B (RAG Knowledge Search)**: In the AI Chatbot, ask `"How do I troubleshoot a VPN connection failure?"`. The assistant responds with grounded instructions citing the *Corporate VPN Connection Troubleshooting Guide*.
- **Scenario C (Self-Healing Agent)**: Navigate to *AI Self-Heal Workflows* and launch *Network Troubleshooting*. Watch the live step-by-step diagnostic probe execution and verify the resolution.
- **Scenario D (Knowledge Management Automation)**: Select a resolved ticket in *All Incidents*, review the resolution notes, and generate a draft runbook article for administrative review.
- **Scenario E (Software Provisioning)**: Request *Visual Studio Code* for instant deployment, or *Docker Desktop Enterprise* to trigger the managerial approval workflow. Switch role to *Administrator* to review and approve the request.
- **Scenario F (Command Center Dashboard)**: Switch role to *Administrator* to inspect live KPI aggregations, category breakdowns, and immutable security audit logs.
