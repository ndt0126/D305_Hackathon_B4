"""Input schemas: raw Discord messages and the daily Bundle.

The intake is deliberately tolerant: the Discord tool is developed by another
person on another machine, so this service normalizes whatever reasonable
shape arrives instead of rejecting it. Accepted at the boundary:

- a bare JSON array of messages;
- a wrapper object under any of `messages` / `bundle` / `data` / `items` /
  `result` / `records`;
- per-message field aliases (`id`/`messageId`, `author`/`username`/`user`,
  `content`/`text`/`message`/`body`, `timestamp`/`time`/`created_at`);
- Discord's raw message object, where `author` is a nested object (both the
  display name and the author's snowflake id are picked up);
- snowflake ids serialized as numbers instead of strings.

Two author fields are kept apart on purpose: `author_id` is the Discord
snowflake — the member's identity, used to group their messages and to build
the `<@id>` mention — while `author_name` is the display name the LLM reads.
The id is optional: exports that only carry names fall back to grouping by
name (see app/core/standup.py).

Everything downstream sees one normalized Bundle.
"""

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

# Wrapper keys commonly used for "the list of messages".
MESSAGE_LIST_KEYS = ("messages", "bundle", "data", "items", "result", "records")

# Field names an export might use for the author's Discord snowflake.
AUTHOR_ID_KEYS = (
    "author_discord_id", "authorDiscordId", "author_id", "authorId",
    "discord_id", "discordId", "user_id", "userId",
)


def _as_str(value: Any) -> Any:
    """Stringify numeric ids; leave anything else for Pydantic to judge."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return str(int(value))
    return value


class DiscordMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message_id: str = Field(validation_alias=AliasChoices("message_id", "id", "messageId"))
    # Display name: what the LLM reads.
    author_name: str = Field(
        validation_alias=AliasChoices("author_name", "author", "username", "user", "authorName")
    )
    # Discord snowflake: the member's identity, and what the tool mentions as
    # <@id>. Optional only so that exports without ids still work.
    author_id: str = Field(default="", validation_alias=AliasChoices(*AUTHOR_ID_KEYS))
    timestamp: datetime = Field(
        validation_alias=AliasChoices("timestamp", "time", "created_at", "createdAt")
    )
    # Empty for attachment-only messages — kept so the author still appears.
    content: str = Field(default="", validation_alias=AliasChoices("content", "text", "message", "body"))
    # Optional: only needed to build clickable Discord message links.
    channel_id: str = Field(default="", validation_alias=AliasChoices("channel_id", "channelId"))
    channel_name: str = Field(default="", validation_alias=AliasChoices("channel_name", "channelName"))

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)

        # Discord's raw message object nests the author; keep name AND id.
        for key in ("author", "user"):
            nested = out.get(key)
            if isinstance(nested, dict):
                out[key] = (
                    nested.get("username") or nested.get("global_name") or nested.get("name") or ""
                )
                if nested.get("id") is not None:
                    out.setdefault("author_id", _as_str(nested["id"]))

        for key in ("id", "message_id", "messageId", "channel_id", "channelId", *AUTHOR_ID_KEYS):
            if key in out:
                out[key] = _as_str(out[key])

        # A payload that carries only an author id still needs a display name.
        name_keys = ("author_name", "author", "username", "user", "authorName")
        if not any(out.get(k) for k in name_keys):
            for key in AUTHOR_ID_KEYS:
                if out.get(key):
                    out["author_name"] = out[key]
                    break
        return out


class Bundle(BaseModel):
    # Optional: required only to build clickable message links.
    guild_id: str = Field(default="", validation_alias=AliasChoices("guild_id", "guildId"))
    # Bundle-level fallback channel for messages without their own channel_id
    # (the export tool typically exports one channel per call).
    channel_id: str = Field(default="", validation_alias=AliasChoices("channel_id", "channelId"))
    # YYYY-MM-DD; when empty, prepare_bundle derives it from the latest message.
    date: str = ""
    channels: list[str] = Field(default_factory=list)
    messages: list[DiscordMessage]

    @model_validator(mode="before")
    @classmethod
    def accept_common_shapes(cls, data: Any) -> Any:
        # A bare array of messages.
        if isinstance(data, list):
            return {"messages": data}
        if not isinstance(data, dict):
            return data

        out = {k: _as_str(v) if k in ("guild_id", "guildId", "channel_id", "channelId") else v
               for k, v in data.items()}
        if "messages" in out:
            return out

        # The message list arrived under some other wrapper key.
        for key in MESSAGE_LIST_KEYS:
            if isinstance(out.get(key), list):
                rest = {k: v for k, v in out.items() if k != key}
                return {**rest, "messages": out[key]}
        return out
