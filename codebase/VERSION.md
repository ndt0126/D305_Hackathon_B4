# Version History

Format: newest first. Bump the version and add an entry for every meaningful
change (feature, contract change, placeholder replaced).

## v0.8 (0.8.0) — 2026-07-30

Members are identified by Discord id, matching the export tool's real shape.

### Fixed
- `author_discord_id` — the field name the export tool actually sends — was
  not in the alias list, so every daily silently fell back to the display
  name and `<@name>` mentions could not resolve. Added it along with
  `authorDiscordId`, `discord_id`, `discordId`.

### Changed
- A member's identity is now their Discord id (falling back to the display
  name only when no id is present), so two accounts sharing a display name
  are no longer merged into one daily.
- The standup prompt refers to members by an opaque `member_key` (m1, m2, …)
  instead of their display name. The model echoes the key back, removing a
  silent failure mode: a mangled Vietnamese display name used to make the
  member's standup unmatchable and therefore cleared.
- `MemberStandup` now carries a `Member` (key, display_name, target_id);
  `format.py` reads `target_id` directly instead of re-deriving it.
- Samples now mirror the real export payload, including `guild_id`,
  `message_id` and `attached_file_urls` (accepted and ignored).

### Verified
- Real OpenAI run on the real export shape: correct snowflakes in
  `target_discord_id`, correct per-member standups, off-topic chatter
  excluded (a member whose only message was about lunch got
  "Không có thông tin."), blockers routed to `weekly.blocked`, zero
  hallucinated evidence ids.

## v0.7 (0.7.0) — 2026-07-30

BREAKING: `dailies[].target_username` renamed to `target_discord_id`, at the
Discord tool owner's request (the tool renders `<@id>` mentions).

### Changed
- `DailyEntry.target_username` → `target_discord_id`, carrying the author's
  Discord snowflake. `meta.sources.dailies` is keyed the same way.
- `DiscordMessage` now separates `author_name` (display name — what the LLM
  reads, and what groups a member's messages) from `author_id` (the Discord
  snowflake). Aliases: `author_id`/`authorId`/`user_id`/`userId`, plus the
  `id` inside Discord's nested author object.
- `target_discord_id` falls back to the display name when the export carries
  no id for that member, so id-less exports keep working instead of 422.
- Samples updated to include `author_id`; `INTEGRATION.md` asks the tool to
  send it, since `<@name>` does not resolve to a mention.

## v0.6 (0.6.0) — 2026-07-30

Tolerant intake, after the partner tool hit repeated 422s in real traffic.

### Added
- The boundary now normalizes instead of rejecting: a bare message array,
  `{"bundle"|"messages"|"data"|"items"|"result"|"records": [...]}`, per-message
  field aliases (`id`/`messageId`, `author`/`username`/`user`, `content`/`text`
  /`body`, `timestamp`/`time`/`created_at`), Discord's nested `author` object,
  numeric snowflake ids, and messages with no content.
- `GET` on the report endpoint answers 405 with a pointer to `GET /health`,
  instead of a bare "Method Not Allowed".
- Rejected request bodies are logged (redacted, truncated) so a partner's
  payload shape can be diagnosed without asking them for it.
- Intake test matrix (`tests/test_intake.py`).

### Fixed
- A 422 response no longer echoes the caller's payload back. Pydantic's
  `input` field made the tool's owner believe the service was returning their
  own request instead of a report; the body now carries only
  `field`/`problem` pairs plus a `hint`.

## v0.5 (0.5.0) — 2026-07-30

BREAKING: output contract replaced per the Discord tool owner's request.

### Changed
- Response is now the tool's contract: `dailies` (per-member
  `target_username`/`yesterday`/`today`) + `weekly`
  (`done`/`doing`/`blocked`/`questions` as newline-joined bullet strings)
  + `meta` (extra traceability block: message-id sources, stats).
- Pipeline rebuilt around two new AI passes: `standup` (per member) and
  `team_summary` (whole team). Removed the topic pipeline
  (`cluster.py`, `resolve.py`, `guardrails.py`) and the delivery/recipients
  concept (`DEFAULT_RECIPIENT_IDS`) — routing is now the tool's job via
  `target_username`.
- Grounding guarantees preserved in code: invented usernames dropped,
  claims/items without real evidence ids stripped, sources exposed in
  `meta.sources`, word caps and secret redaction on all output text.

### Added
- Agreed anti-fabrication empty states: "Không có vấn đề được thảo luận."
  (empty weekly bucket) and "Không có thông tin." (member field without
  signal).
- Grounding test suite with a stub LLM (`tests/test_grounding.py`).
- `INTEGRATION.md`: the contract handed to the Discord tool's owner
  (endpoint, auth header, request/response samples, error table).

### Verified
- Real OpenAI path exercised for the first time (`USE_MOCK_LLM=false`):
  HTTP 200 in ~6s for a 6-message day, two tool calls, Vietnamese output,
  off-topic chatter correctly excluded, empty states applied.
- Public Cloudflare Tunnel reachable from outside: `/health` returns 200 and
  an unauthenticated POST correctly returns 401 through the tunnel.

## v0.4 (0.4.0) — 2026-07-30

Public deployment support (Cloudflare Tunnel).

### Added
- Optional inbound auth (`app/api/security.py`): when `SERVICE_API_KEY` is
  set in `.env`, both report endpoints require the same value in the
  `X-API-Key` header (401 otherwise). Empty key = no auth (local dev).
  `/health` always stays open for tunnel checks.
- README section on exposing the service via a Cloudflare Tunnel.

## v0.3 (0.3.0) — 2026-07-30

Finalize the LLM layer: Vietnamese prompts and schema-enforced outputs.

### Added
- Function-calling tools (`app/llm/tools.py`): each pipeline pass forces a
  tool call whose parameters mirror the expected JSON, so the OpenAI API
  validates the output shape. The tool is selected from the prompt's
  "TASK:" marker; unknown tasks fall back to plain JSON mode.
- Prompt/tool contract tests (`tests/test_llm.py`).

### Changed
- System prompt and task prompts rewritten in Vietnamese (the team chats and
  reports in Vietnamese); technical JSON values stay in English to match the
  code enums. `DEFAULT_SYSTEM_PROMPT` renamed to `SYSTEM_PROMPT` — no longer
  a placeholder, still overridable via `SYSTEM_PROMPT_FILE`.
- `app/integrations/discord_export.py` docstring now carries a concrete
  checklist of what to request from the export tool's owner.
- `.env.example` documents how to obtain Discord user ids for
  `DEFAULT_RECIPIENT_IDS` (Developer Mode → Copy User ID).

## v0.2 (0.2.0) — 2026-07-30

Align with the Discord export tool's confirmed response format; focus the
assistant on daily work/study reporting.

### Added
- Input support for the export tool's raw format: a bare JSON array of
  messages with `id`, `author`, `content`, `timestamp` (field aliases on the
  same schemas; sample in `data/samples/sample_tool_export_input.json`).
- Bundle-level `channel_id` fallback and report `date` derivation from the
  latest message when the export format omits them.
- Secret redaction guardrail (`app/core/redact.py`): API keys, tokens and
  `password:`/`api_key:` assignments are stripped from report quotes,
  summaries and titles.

### Changed
- System prompt narrowed to a single job: summarize the previous day's WORK
  and STUDY content (tasks, progress, blockers, decisions, deadlines) and
  explicitly exclude personal information, small talk and credentials.
- Cluster prompt now only creates work/study clusters.
- `message_link` is best-effort: empty when `guild_id`/`channel_id` are not
  available (the export tool's format carries neither).

## v0 (0.1.0) — 2026-07-30

Initial base version.

### Added
- FastAPI service with `POST /api/v1/reports/generate` (push mode),
  `POST /api/v1/reports/generate-from-export` (pull mode, placeholder) and
  `GET /health`.
- Core pipeline (`app/core/`): bundle preparation -> topic clustering
  (AI pass 1) -> resolved/unresolved decision (AI pass 2) -> deterministic
  guardrails -> report formatting with Discord message links.
- OpenAI integration (`app/llm/client.py`) plus a deterministic offline mock
  (`USE_MOCK_LLM=true`) for tests and demos without an API key.
- Pydantic schemas for input bundles and the structured `ReportDraft` output,
  including delivery instructions (`draft_for_review`, user/role recipients).
- CLI (`python -m app.cli`) running the same pipeline without a server.
- Configuration via `.env` (pydantic-settings), central logging, structured
  error handling (502 for LLM/export failures, 422 for validation).
- Sample input/output data in `data/samples/`, offline test suite (pytest).

### Placeholders (to be replaced in later versions)
- Confidential Discord export endpoint (`app/integrations/discord_export.py`).
- Detailed production system prompt (`app/llm/prompts.py`).
- Function-calling tool definitions (`app/llm/tools.py`, empty).
- Default report-writer recipient ids (`DEFAULT_RECIPIENT_IDS`).
