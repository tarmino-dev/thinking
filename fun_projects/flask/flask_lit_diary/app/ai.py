"""Claude-backed helper for discussing a note with its author.

A thin module (no service layer): it builds a system prompt from a note and sends
the conversation to the Claude API via the official `anthropic` SDK, which reads
ANTHROPIC_API_KEY from the environment.
"""

import html
import re

import anthropic

CHAT_MODEL = "claude-haiku-4-5"
MAX_TOKENS = 1024
# Cap how much of the note body is sent, to bound token cost.
MAX_BODY_CHARS = 4000

_client = None


def _get_client():
    """Lazily create the Anthropic client (reads ANTHROPIC_API_KEY from env)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _strip_html(text):
    """Reduce CKEditor HTML to plain text for the prompt."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _system_prompt(note):
    """Build the system prompt describing the note under discussion."""
    body = _strip_html(note.body)[:MAX_BODY_CHARS]
    lines = [
        "You are a thoughtful reading companion. The user wants to discuss their "
        "own reading note with you. Be concise, ask good questions, and help them "
        "reflect. Respond in the same language the user writes in.",
        "",
        "The note under discussion:",
        f"Title: {note.title}",
        f"Subtitle: {note.subtitle}",
    ]
    if note.book:
        lines.append(f"Book: {note.book}")
    lines.append(f"Content: {body}")
    return "\n".join(lines)


def discuss_note(note, history):
    """Send the conversation to Claude and return the assistant's reply text.

    `history` is a list of {"role": "user"|"assistant", "content": str}. Raises
    anthropic.AnthropicError on API failure (the caller maps it to a JSON error).
    """
    response = _get_client().messages.create(
        model=CHAT_MODEL,
        max_tokens=MAX_TOKENS,
        system=_system_prompt(note),
        messages=history,
    )
    return next((block.text for block in response.content if block.type == "text"), "")
