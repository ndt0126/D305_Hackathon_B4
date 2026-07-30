# Daily Report Assistant — Backend Service ("the brain")

Receives one day of exported Discord messages from the team's Discord tool,
uses an LLM to build **per-member standups** (`dailies`) and a **team-level
summary** (`weekly`: done / doing / blocked / questions), and returns the
result as JSON in the exact contract the Discord tool renders and delivers.

## Architecture

```
Discord tool (coworker) ──POST messages──▶ this service ──dailies+weekly JSON──▶ Discord tool
      "hands & eyes"                          "brain"                        renders & notifies
                                                 │
                                                 ▼
                                          OpenAI (or mock)
```

```
codebase/
├── app/
│   ├── main.py              FastAPI entry point (uvicorn app.main:app)
│   ├── cli.py               Same pipeline without a server (eval / live demo)
│   ├── config.py            Settings from env vars / .env
│   ├── logging_config.py    Logging setup
│   ├── api/
│   │   ├── routes.py        /health, /api/v1/reports/*
│   │   ├── security.py      Optional X-API-Key auth (public deployment)
│   │   └── errors.py        Structured error responses
│   ├── schemas/
│   │   ├── messages.py      Input: DiscordMessage, Bundle (tool format accepted)
│   │   └── report.py        Output: ToolReport (dailies + weekly + meta)
│   ├── core/                Pure pipeline — no FastAPI/OpenAI/HTTP imports
│   │   ├── interfaces.py    LLMClient protocol (implementations injected)
│   │   ├── bundle.py        Normalize exported messages, derive date/channel
│   │   ├── standup.py       AI pass 1: per-member yesterday/today + evidence
│   │   ├── summary.py       AI pass 2: team done/doing/blocked/questions
│   │   ├── redact.py        Strip secrets (API keys, tokens) from output text
│   │   ├── format.py        Word caps, empty-state texts, assemble ToolReport
│   │   └── pipeline.py      Orchestrates all stages
│   ├── llm/
│   │   ├── prompts.py       All prompt text (Vietnamese, overridable via .env)
│   │   ├── tools.py         Function-calling schemas (enforce output shape)
│   │   ├── client.py        OpenAI client (forced tool calls) + factory
│   │   └── mock_client.py   Deterministic offline mock (tests/demo)
│   └── integrations/
│       └── discord_export.py  Export API client (PLACEHOLDER, pull mode)
├── data/samples/            Sample input (tool format) + sample output
├── tests/                   Offline tests (pytest, mock/stub LLM)
├── .env.example             All configuration, documented
├── VERSION.md               Version history / changelog
└── requirements.txt
```

## Setup

```powershell
cd codebase
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env      # then edit .env
```

On macOS/Linux use `.venv/bin/python` and `cp` instead.

## Run

**API server:** `.venv\Scripts\python -m uvicorn app.main:app --port 8000`
(Swagger UI at http://127.0.0.1:8000/docs)

**CLI (no server, same pipeline):**
`.venv\Scripts\python -m app.cli --input data/samples/sample_tool_export_input.json --mock`

**Tests:** `.venv\Scripts\python -m pytest`

## API contract

### `POST /api/v1/reports/generate`

Request — `bundle` accepts either a full Bundle object or the Discord tool's
raw export: a bare JSON array of `{id, author, content, timestamp}`
([sample](data/samples/sample_tool_export_input.json)):

```json
{ "bundle": [ { "id": "153...", "author": "Trung", "content": "...", "timestamp": "2026-07-26T02:12:53.754Z" } ] }
```

Response ([full sample](data/samples/sample_report_output.json)):

```json
{
  "dailies": [
    { "target_discord_id": "840393744107831359", "yesterday": "...", "today": "..." }
  ],
  "weekly": {
    "done": "- ...", "doing": "...", "blocked": "...", "questions": "- ..."
  },
  "meta": { "report_id": "...", "stats": {...}, "sources": {...} }
}
```

- `target_discord_id` is the author's Discord snowflake from the input, so
  the tool can mention them as `<@id>`; it falls back to the display name
  when the export carries no id for that member.
- Multi-item `weekly` buckets are newline-joined `- item` lines.
- `meta` is extra traceability data (message-id sources per claim) used by
  our eval — the tool can ignore it.

**Agreed empty-state rule (no fabrication):** no signal for a weekly bucket →
`"Không có vấn đề được thảo luận."`; no signal for a member's field →
`"Không có thông tin."`.

### `POST /api/v1/reports/generate-from-export` (pull mode, PLACEHOLDER)

`{ "date": "2026-07-26" }` — fetches the bundle from the coworker's export
API first. Non-functional until that confidential endpoint is configured
(checklist in `app/integrations/discord_export.py`).

## Public deployment (Cloudflare Tunnel)

The service can be exposed publicly so the Discord tool can call it from
anywhere, e.g. a Cloudflare Tunnel forwarding `https://<your-domain>` to
`http://127.0.0.1:8000`. Checklist:

1. Set `SERVICE_API_KEY` in `.env` to a long random string
   (`python -c "import secrets; print(secrets.token_urlsafe(32))"`) —
   without it, anyone who finds the URL can spend your OpenAI budget.
2. Start the service on the tunneled port and keep `cloudflared` running.
3. Verify from outside: `curl https://<your-domain>/health` → `{"status":"ok"}`.
4. Give the tool's owner: the public URL, the `X-API-Key` value (privately),
   and the request/response contract above.

## Guarantees enforced in code (not prompts)

- A username the model invents is dropped; every real author appears.
- Any claim/item without at least one evidence id that exists in the input
  is stripped; sources are reported in `meta.sources` for eval.
- Empty results use the agreed empty-state texts instead of invented content.
- Each field/item is capped at 25 words.
- Secrets pasted into chat (API keys, tokens, `password:`/`api_key:`
  assignments) are removed from all output text (`app/core/redact.py`).

> Note for the tool side: the brain's output is a **draft**. The tool should
> let the report writer review/edit before anything is forwarded to mentors —
> that responsibility now lives entirely in the tool's UI.
