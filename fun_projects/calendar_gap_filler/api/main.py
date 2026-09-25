"""HTTP layer: exposes core.suggest_events() and feedback_module.store over
HTTP, and serves the static UI (ui/index.html) that talks to both.

Deliberately thin — this module's only job is translating between the
internal orchestrator/storage and the wire format (Pydantic response
models + HTTP status codes) or, for /ui, just handing back static files.
All real logic still lives in core.py and the modules it composes; nothing
here should duplicate that.

Run locally with:
    uvicorn api.main:app --reload
Then open http://127.0.0.1:8000/ui in a browser.
"""

import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

from calendar_module.gaps import Gap
from classifier_module.ranking import RankedEvent
from config import GOOGLE_TOKEN_FILE
from core import suggest_events
from feedback_module.store import record_feedback

app = FastAPI(title="Calendar Gap Filler")

# "ui" is relative to the current working directory, same as every path in
# config.py (token.json, profile.json, feedback.db) — assumes the app is
# started from the project root, as README.md's "Running the API" section
# already documents. html=True makes GET /ui/ serve ui/index.html.
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")


class EventResponse(BaseModel):
    """Wire format for a single suggested event. Field names and types
    mirror events_module.client.Event — from_attributes lets Pydantic read
    them straight off the dataclass via model_validate(), so there's no
    manual field-by-field mapping to keep in sync by hand.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    start: datetime
    duration_minutes: float | None
    classification: str | None
    description: str | None
    venue_name: str | None
    url: str | None


class RankedEventResponse(BaseModel):
    """Wire format for classifier_module.ranking.RankedEvent."""

    model_config = ConfigDict(from_attributes=True)

    event: EventResponse
    score: float


class GapResponse(BaseModel):
    """Wire format for calendar_module.gaps.Gap."""

    model_config = ConfigDict(from_attributes=True)

    start: datetime
    end: datetime
    duration_minutes: float


class SuggestionResponse(BaseModel):
    """One free time slot paired with its ranked event suggestions.

    suggest_events() returns this as a (Gap, list[RankedEvent]) tuple; a
    tuple has no attribute names, so it can't go through model_validate()
    like the pieces inside it can — it gets reshaped into a named JSON
    object by _to_response() below instead of serializing as an unlabeled
    nested array.
    """

    gap: GapResponse
    suggestions: list[RankedEventResponse]


def _to_response(gap: Gap, ranked: list[RankedEvent]) -> SuggestionResponse:
    return SuggestionResponse(
        gap=GapResponse.model_validate(gap),
        suggestions=[RankedEventResponse.model_validate(r) for r in ranked],
    )


@app.get("/suggestions", response_model=list[SuggestionResponse])
def get_suggestions() -> list[SuggestionResponse]:
    """Return this week's free time slots paired with ranked local event
    suggestions for each — the same pipeline as scripts/check_suggestions.py,
    over HTTP instead of the terminal.
    """
    if not os.path.exists(GOOGLE_TOKEN_FILE):
        # Without a cached token, calendar_module.client would try to open
        # an interactive browser OAuth flow right here, inside the request
        # handler — fine for a CLI script run by hand, but it would just
        # hang an HTTP client waiting for someone to click through a login
        # screen on this machine. Fail fast instead: token.json only gets
        # created by completing that flow once via a CLI entry point (see
        # README), which is a one-time setup step, not something the API
        # should ever attempt on a caller's behalf.
        raise HTTPException(
            status_code=503,
            detail=(
                f"Google Calendar isn't authenticated yet ({GOOGLE_TOKEN_FILE} not found). "
                "Run any script in scripts/ once locally to complete the browser login, then retry."
            ),
        )

    try:
        suggestions = suggest_events()
    except RuntimeError as error:
        # core.py and the modules it composes raise RuntimeError for every
        # "you forgot to configure X" case (missing .env values, an expired
        # Google token, a missing profile.json, ...). 503 reads accurately
        # here: this isn't a bad request, it's a server that isn't
        # configured yet.
        raise HTTPException(status_code=503, detail=str(error)) from error

    return [_to_response(gap, ranked) for gap, ranked in suggestions]


class FeedbackRequest(BaseModel):
    """Request body for POST /feedback: a snapshot of a suggested event
    (as the client received it from GET /suggestions) plus whether the
    user liked it. Mirrors feedback_module.store.record_feedback()'s
    parameters — see that function and architecture.md decision #7 for
    why a full snapshot is stored instead of just event_id.
    """

    event_id: str
    event_name: str
    event_start: datetime
    # Cosine similarity (classifier_module.ranking) is mathematically
    # bounded to [-1, 1] — this isn't an arbitrary business rule, it's a
    # real property of the value, so it's enforced here rather than left
    # for record_feedback() to silently accept anything.
    score: float = Field(ge=-1.0, le=1.0)
    liked: bool
    # Added in Phase 10 step 3 (decision #12) so classifier_module's
    # feedback-based ranking has a feature to train on later. Optional
    # (defaults to None) because events_module.client.Event.classification
    # itself is often None (Ticketmaster doesn't always provide one).
    classification: str | None = None

    @field_validator("event_start")
    @classmethod
    def _event_start_must_be_timezone_aware(cls, value: datetime) -> datetime:
        # Same requirement as everywhere else in this app (calendar_module,
        # events_module, feedback_module.store) — enforced here, at the
        # request boundary, so a bad request fails with a clear 422 instead
        # of reaching record_feedback()'s own check and raising a raw
        # ValueError that FastAPI would turn into an opaque 500.
        if value.tzinfo is None:
            raise ValueError("event_start must be timezone-aware")
        return value


class FeedbackCreatedResponse(BaseModel):
    """Response body for POST /feedback: the id of the newly created row."""

    id: int


@app.post("/feedback", response_model=FeedbackCreatedResponse, status_code=201)
def post_feedback(feedback: FeedbackRequest) -> FeedbackCreatedResponse:
    """Record whether the user liked a suggested event.

    Expected to be called after GET /suggestions, with the client sending
    back the same event snapshot and score it received plus a like/dislike.
    """
    feedback_id = record_feedback(
        event_id=feedback.event_id,
        event_name=feedback.event_name,
        event_start=feedback.event_start,
        score=feedback.score,
        liked=feedback.liked,
        classification=feedback.classification,
    )
    return FeedbackCreatedResponse(id=feedback_id)
