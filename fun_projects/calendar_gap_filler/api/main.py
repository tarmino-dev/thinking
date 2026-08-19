"""HTTP layer: exposes core.suggest_events() over a single GET endpoint.

Deliberately thin — this module's only job is translating between the
internal orchestrator and the wire format (Pydantic response models + HTTP
status codes). All real logic still lives in core.py and the modules it
composes; nothing here should duplicate that.

Run locally with:
    uvicorn api.main:app --reload
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from calendar_module.gaps import Gap
from classifier_module.ranking import RankedEvent
from core import suggest_events

app = FastAPI(title="Calendar Gap Filler")


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
