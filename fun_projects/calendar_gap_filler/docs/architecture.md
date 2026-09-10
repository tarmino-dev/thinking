# Architecture

## Overview

Calendar Gap Filler is a personal, single-user assistant that finds empty time
slots in a Google Calendar and suggests locally relevant events to fill them,
ranked against the user's interest profile by a lightweight ML model.

## Current status

Phases 1-7 are all complete: Calendar Module, Event Source Module, Profile
Module, ML Ranking Module, the Orchestrator (`core.py`) that wires all
four together into one real pipeline, the API Layer (`api/main.py`), and
`feedback_module/` for storing user feedback — `suggest_events()` loads
the profile, finds this week's calendar gaps, fetches nearby events once,
embeds everything once via TinyBERT, and returns each gap paired with its
top-ranked event suggestions; `GET /suggestions` wraps that same pipeline
as JSON, with a `503` instead of a hang or a crash when the app isn't
configured or authenticated yet; `POST /feedback` records a like/dislike
on a suggested event into a local SQLite database (see decision #7 for
why only feedback is persisted for now, not the profile or a cache of
fetched events). Every module is covered by unit tests and has been
verified end-to-end against real data (`scripts/check_suggestions.py` for
the pipeline, `uvicorn api.main:app` + curl/Swagger for both API
endpoints). Minimal UI (Phase 8) is next. This document describes the
target architecture the code is growing into, module by module, per the
roadmap below, and is updated as each module is actually built.

## Modules (planned)

Flat, package-per-concern structure. No service/repository/factory layers —
each module has one clear responsibility, and a thin orchestrator wires them
together.

| Module | Responsibility | Notes |
|---|---|---|
| `calendar_module/` | Reads the user's Google Calendar (read-only) and computes free time slots ("gaps"). | Split into `client.py` (Google Calendar API access) and `gaps.py` (pure gap-finding logic, no I/O, easy to unit test). |
| `events_module/` | Fetches candidate local events. | Uses the Ticketmaster Discovery API; normalizes results into a common `Event` shape. `Event.duration_minutes` is often `None` — Ticketmaster frequently doesn't provide an event's end time. `Event.start` is converted from Ticketmaster's UTC timestamps to local system time at parse time, so it lines up with `Gap.start`/`Gap.end` (already local) for both comparisons and display — comparisons work regardless, but mixed timezones make printed output confusing. |
| `profile_module/` | Holds the user's interest profile. | Simple in-memory structure at first; no database yet. |
| `classifier_module/` | Ranks candidate events against the user's interest profile. | TinyBERT embeddings via `sentence-transformers` (`paraphrase-TinyBERT-L6-v2`), ranked by cosine similarity, filtered by gap duration. |
| `orchestrator` (`core.py`) | Single composition point: gaps -> candidate events -> ranked suggestions. | Deliberately not a separate "service layer". |
| `api/` | Exposes the orchestrator over HTTP, and accepts feedback on suggestions. | FastAPI, two routes: `GET /suggestions` and `POST /feedback`. Pydantic response models (`SuggestionResponse` etc.) decouple the wire format from internal dataclasses via `model_validate(..., from_attributes=True)`; `FeedbackRequest` validates at the request boundary (timezone-aware `event_start`, `score` constrained to `[-1, 1]`) so bad input fails with `422` before ever reaching `feedback_module.store`. `GET /suggestions` returns `503` (not a 500 or a hang) when the app isn't configured or authenticated yet — see decision #1 for the missing-`token.json` case specifically. |
| `feedback_module/` | Stores user feedback (like/dislike) on suggested events. | SQLite via stdlib `sqlite3`, no ORM — `init_db()` creates the table if missing, `record_feedback()` writes one denormalized row (event snapshot + ranking score + like/dislike) and returns its id. Scope narrowed from the original "cached events + profile + feedback" plan to feedback only — see decision #7. Write-only for now, no `GET /feedback` (same decision) — inspect with the `sqlite3` CLI during development. |

## Key architectural decisions

1. **Calendar integration**: Google Calendar API via OAuth2 (Installed App
   flow), scope `calendar.readonly`. Single-user; the app only reads and
   suggests, it never writes to the calendar. Chosen over a secret `.ics`
   feed URL because the product needs near-real-time availability, which the
   `.ics` export does not reliably provide. The official API is also the
   standard, well-supported path and leaves room to add multi-user OAuth
   later without redesigning this module. Known trade-off: since the OAuth
   consent screen is in "Testing" status (see README setup), Google expires
   the refresh token after 7 days no matter how often it's used — expect
   `token.json` to need regenerating (delete it, rerun, log in via browser
   again) roughly weekly. `calendar_module.client` raises a clear
   `RuntimeError` when this happens rather than the raw Google error.
   Switching to "Production" status would remove this, at the cost of
   going through Google's app verification — not worth it for a
   single-user personal tool. Separate hard-won fact, found while building
   the API layer (Phase 6): `calendar_module.client._load_credentials()`
   only raises `RuntimeError` for an *expired* token — if `token.json` is
   missing entirely, it instead opens an interactive browser OAuth flow
   and blocks until someone logs in. That's the intended first-run
   experience for the CLI scripts, but inside an HTTP request handler it
   would just hang the caller with no response at all. Rather than change
   `calendar_module.client`'s CLI-friendly behavior, `api/main.py` checks
   `GOOGLE_TOKEN_FILE` exists *before* calling into the orchestrator and
   returns a normal `HTTPException(503)` if not — the interactive flow
   still only ever runs from a CLI script, never from the API.
2. **Event source**: Ticketmaster Discovery API (free tier, purpose-built for
   event discovery) over Eventbrite (organizer/ticketing focused, not
   discovery focused) and scraping (fragile, legally murky, unnecessary
   complexity for an MVP).
3. **ML ranking**: `sentence-transformers` with a pretrained TinyBERT
   checkpoint (`paraphrase-TinyBERT-L6-v2`) for sentence embeddings, ranked
   by cosine similarity against the user's interest profile. No fine-tuning
   at this stage — revisit only if off-the-shelf ranking quality proves
   insufficient. Note: PyTorch stopped publishing pip wheels for Intel
   macOS (x86_64) after `torch==2.2.2` (deprecation announced Jan 2024).
   Since current `transformers`/`sentence-transformers` require
   `torch>=2.5`, Intel Mac setups must use the pinned, known-working trio
   in `requirements.txt` (`torch==2.2.2`, `transformers==4.38.2`,
   `sentence-transformers==2.5.1`, `numpy<2`) instead of the latest
   releases. Note: real-world cosine similarity scores from TinyBERT (and
   BERT-style sentence embeddings generally) cluster in a narrow,
   compressed range rather than spanning the full [-1, 1] — a well-known
   characteristic of these models (sometimes called embedding
   "anisotropy"), confirmed on this project's own data via
   `scripts/check_ranking.py` (scores landed around 0.14-0.30 for real
   events). The practical consequence: treat scores as a *relative*
   ranking signal (this event beats that one) — never compare against a
   fixed absolute threshold like "only show score > 0.5", since a
   genuinely great match may never reach that number. `rank_events()`
   already only sorts, it doesn't filter by a threshold, which turns out
   to be the right call for this reason.
4. **Web framework**: FastAPI — typed, low-boilerplate, built-in docs.
   Route handlers are plain sync `def`, not `async def`: this decision was
   originally written down as "async-friendly for outbound calls", but
   when Phase 6 actually got built, every underlying call
   (`google-api-python-client`, `requests`, `sentence-transformers`) turned
   out to be fully synchronous with no async variant available — so
   `async def` would just add a layer that buys nothing. FastAPI already
   runs sync routes in a threadpool, which is plenty for a single-user app.
5. **Storage**: SQLite for the MVP; migration to Postgres deferred to the
   deployment phase.
6. **Event search geolocation**: `latlong` + `radius` query params on the
   Ticketmaster Discovery API, over `postalCode` (format varies too much
   between countries) or `geoPoint` (Ticketmaster's newer, non-deprecated
   option, but requires geohash-encoding the user's coordinates — an extra
   dependency for no real benefit at our scale). Risk: `latlong` is marked
   deprecated in Ticketmaster's docs and could be removed in a future API
   version, at which point we'd need to switch to `geoPoint`. Note:
   `radius` must be sent as an integer (error `DIS1014` otherwise) even
   though Ticketmaster's own docs list it as a generic String —
   `events_module.client.search_events` rounds it before sending.
7. **Persistence scope (Phase 7)**: only user feedback (like/dislike on a
   suggested event) gets a database table for now — not the interest
   profile, not a cache of fetched events, despite both being mentioned in
   earlier roadmap notes. Neither `profile.json` nor the live per-request
   Ticketmaster fetch has shown an actual limitation (personal single-user
   app, occasional requests, well within Ticketmaster's free-tier rate
   limit) — moving either into SQLite now would be a refactor without a
   driving need. Feedback is different: there is currently no way to
   record it at all, and it's a hard prerequisite for the feedback loop
   already planned for Phase 10. Storage is plain stdlib `sqlite3` — no
   ORM, one table, one write path. No read endpoint yet either
   (`GET /feedback` is deferred until Phase 10 or a UI actually needs to
   read it back; the `sqlite3` CLI is enough to verify it during
   development). Each row denormalizes a snapshot of the event (`event_id`,
   `event_name`, `event_start`, and the ranking `score` at the time it was
   shown) instead of storing only `event_id`, because no event cache
   exists — without the snapshot, a liked event could become unrecoverable
   the moment Ticketmaster stops returning it.

## Roadmap (high level)

| # | Phase | Status |
|---|---|---|
| 1 | Calendar Module | Done |
| 2 | Event Source Module (Ticketmaster integration) | Done |
| 3 | Profile Module | Done |
| 4 | ML Ranking Module (TinyBERT embeddings) | Done |
| 5 | Orchestrator | Done |
| 6 | API Layer (FastAPI) | Done |
| 7 | Persistence (SQLite) | Done — scope narrowed to feedback only, not profile/cached events too (see decision #7); `docs/er_diagram.mermaid` has its first real content |
| 8 | Minimal UI | Not started — format tbd |
| 9 | Deployment (Docker + hosting, public URL) | Not started |
| 10 | Hardening (error handling, logging, feedback loop) | Not started |

Each phase is broken into its own commits as it's implemented; the commit
history is the source of truth for the actual sequence and timing.
