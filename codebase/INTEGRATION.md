# Integration guide for the Discord tool ("hands" → "brain")

Everything the Discord tool needs in order to send messages to this service
and receive the report payload. Verified working end to end on 2026-07-30
(public tunnel, real OpenAI call, ~6s round trip for a 6-message day).

## Endpoint

```
POST https://agent.dquangminh2003.id.vn/api/v1/reports/generate
Content-Type: application/json
X-API-Key: <sent to you privately — never commit it>
```

Health check (no auth, safe to poll): `GET https://agent.dquangminh2003.id.vn/health`
→ `{"status":"ok"}`

## Request

Send the raw export array — the same `{id, author, content, timestamp}`
objects the export tool already produces, no reshaping needed:

```json
[
  {
    "id": "1531909320521027636",
    "guild_id": "1530038187022352464",
    "channel_id": "1530038187022352467",
    "message_id": "1531909320521027636",
    "author": "dquangminh.",
    "author_discord_id": "710120883556974612",
    "content": "e commit bản mới nhất r nha",
    "attached_file_urls": [],
    "timestamp": "2026-07-29T06:20:43.511Z"
  }
]
```

This is the export tool's own shape, sent as-is — verified end to end on
2026-07-30. `attached_file_urls` and the extra id fields are accepted and
ignored (reading attachments is out of scope).

> `author_discord_id` is the member's identity: it groups their messages and
> comes back as `dailies[].target_discord_id` for the `<@id>` mention. Two
> accounts sharing a display name therefore stay separate. Discord's nested
> `"author": {"id": …, "username": …}` object works too. Without any id the
> service falls back to the display name — nothing breaks, but `<@name>` will
> not ping anyone.

**The intake is tolerant — all of these work**, so there is no need to match
one exact shape:

| Envelope | Accepted |
|---|---|
| bare array `[ ... ]` | yes |
| `{"bundle": [ ... ]}` | yes |
| `{"messages": [ ... ]}` / `{"data": [ ... ]}` / `{"items": [ ... ]}` | yes |
| extra top-level fields such as `date`, `guild_id` | ignored unless known |

| Per-message field | Accepted names |
|---|---|
| id | `id`, `message_id`, `messageId` — string or number |
| author name | `author`, `username`, `user`, `author_name` — plain string, or Discord's nested `{"id":…, "username":…}` object |
| author id | `author_discord_id`, `authorDiscordId`, `author_id`, `authorId`, `discord_id`, `discordId`, `user_id`, `userId` — string or number; also read from a nested author object |
| content | `content`, `text`, `message`, `body` — may be absent |
| timestamp | `timestamp`, `time`, `created_at`, `createdAt` — ISO 8601 |
| channel (optional) | `channel_id`, `channelId` |

- The report date is derived from the latest message unless an explicit
  `date` is sent.
- Send one day of public channel messages per request.

## Response (HTTP 200)

```json
{
  "dailies": [
    {
      "target_discord_id": "982314567890123456",
      "yesterday": "Em commit bản mới nhất và tóm tắt khảo sát đã đăng.",
      "today": "Mai em làm tiếp phần eval với golden set."
    },
    {
      "target_discord_id": "710120883556974612",
      "yesterday": "Không có thông tin.",
      "today": "Không có thông tin."
    }
  ],
  "weekly": {
    "done": "- Đã commit bản mới nhất và tóm tắt khảo sát.",
    "doing": "- Đang làm phần eval với golden set.",
    "blocked": "- Bị lỗi timeout khi gọi API export.\n- Cần người hỗ trợ fix lỗi trước deadline.",
    "questions": "Không có vấn đề được thảo luận."
  },
  "meta": { "report_id": "rpt_2026-07-26", "stats": {}, "sources": {} }
}
```

- `target_discord_id` is the `author_discord_id` that was sent in, ready for
  `<@id>`. When a member's messages carried no id, it holds their display
  name instead — worth checking for digits before building a mention.
- One entry per member who posted that day, in first-appearance order.
  Members with no work/study signal are still listed, with the
  "Không có thông tin." text (see below), so nobody is silently skipped.
- `weekly` values are plain strings; multiple items are newline-joined
  `- item` lines, ready to drop into a Discord embed field.
- `meta` is extra traceability data (which message ids back each claim) used
  by our evaluation. **The tool can ignore it entirely.**

### Empty states (never invented content)

When the messages contain no usable signal, the service says so explicitly
instead of making something up. Render these strings as-is:

| Field | Value when there is no signal |
|---|---|
| a `weekly` bucket | `Không có vấn đề được thảo luận.` |
| `yesterday` / `today` | `Không có thông tin.` |

## Errors

| Status | Meaning | What to do |
|---|---|---|
| 401 | `X-API-Key` missing or wrong | Check the header value |
| 405 | Wrong HTTP method (a `GET` on this path) | Use `POST`; for liveness checks use `GET /health` |
| 422 | Body still unusable after normalization | Read `detail[].field` / `detail[].problem` and `hint` |
| 502 | Upstream LLM call failed | Retry once; body is `{"error": "llm_error", "detail": "..."}` |
| 500 | Unexpected server error | Report it with the timestamp so we can check logs |
| Cloudflare 502/1033 | The brain or the tunnel is not running | Ping the brain's owner |

A 422 body names the offending fields and never mirrors the request back:

```json
{
  "error": "invalid_request_body",
  "detail": [{ "field": "bundle.messages.0.timestamp", "problem": "Field required" }],
  "hint": "Send the messages as a bare JSON array, or wrapped as ..."
}
```

## Two things to keep in mind

1. **The service runs on a laptop behind a Cloudflare Tunnel.** It answers
   only while both `uvicorn` and `cloudflared` are up. Ping before a demo.
2. **The output is a draft, not a finished report.** Let the report writer
   review and edit it before anything reaches a mentor — a wrong report that
   has already been sent cannot be taken back. That review step now lives
   entirely in the tool's UI.
