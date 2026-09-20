# Architecture

## Overview

Calendar Gap Filler is a personal, single-user assistant that finds empty time
slots in a Google Calendar and suggests locally relevant events to fill them,
ranked against the user's interest profile by a lightweight ML model.

## Current status

Phases 1-9 are all complete: Calendar Module, Event Source Module, Profile
Module, ML Ranking Module, the Orchestrator (`core.py`) that wires all
four together into one real pipeline, the API Layer (`api/main.py`),
`feedback_module/` for storing user feedback, a minimal UI
(`ui/index.html`), and deployment (Docker, local-only — see decision #9)
— `suggest_events()` loads the profile, finds this
week's calendar gaps, fetches nearby events once, embeds everything once
via TinyBERT, and returns each gap paired with its top-ranked event
suggestions; `GET /suggestions` wraps that same pipeline as JSON, with a
`503` instead of a hang or a crash when the app isn't configured or
authenticated yet; `POST /feedback` records a like/dislike on a suggested
event into a local SQLite database (see decision #7 for why only feedback
is persisted for now, not the profile or a cache of fetched events); and
`GET /ui/` serves a single static page, from the same FastAPI app, that
calls both of those endpoints so suggestions can be viewed and reacted to
without curl or Swagger. Every module is covered by unit tests and has
been verified end-to-end against real data (`scripts/check_suggestions.py`
for the pipeline, `uvicorn api.main:app` + a browser at `/ui/` for the
full loop, and `docker compose up --build` for the deployed path). Hardening
(Phase 10) is next. This document describes the
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
| `api/` | Exposes the orchestrator over HTTP, accepts feedback on suggestions, and serves the static UI. | FastAPI, two JSON routes (`GET /suggestions`, `POST /feedback`) plus a `StaticFiles` mount at `/ui` serving `ui/`. Pydantic response models (`SuggestionResponse` etc.) decouple the wire format from internal dataclasses via `model_validate(..., from_attributes=True)`; `FeedbackRequest` validates at the request boundary (timezone-aware `event_start`, `score` constrained to `[-1, 1]`) so bad input fails with `422` before ever reaching `feedback_module.store`. `GET /suggestions` returns `503` (not a 500 or a hang) when the app isn't configured or authenticated yet — see decision #1 for the missing-`token.json` case specifically. |
| `feedback_module/` | Stores user feedback (like/dislike) on suggested events. | SQLite via stdlib `sqlite3`, no ORM — `init_db()` creates the table if missing, `record_feedback()` writes one denormalized row (event snapshot + ranking score + like/dislike) and returns its id. Scope narrowed from the original "cached events + profile + feedback" plan to feedback only — see decision #7. Write-only for now, no `GET /feedback` (same decision) — inspect with the `sqlite3` CLI during development. |
| `ui/` | A single-page UI for viewing this week's suggestions and giving feedback. | Static `index.html` (no build step), served by `api/main.py` via `StaticFiles` at `/ui`. Fetches `GET /suggestions` on load (shows a loading state, and the `503` `detail` message directly if the app isn't ready yet); shows gaps with no fitting events too, not just ones with suggestions (matches `scripts/check_suggestions.py`'s convention). Each suggestion's 👍/👎 buttons `fetch POST /feedback` using the event/score already in hand (no extra request) and then disable themselves — `feedback_module.store` has no update path, so re-voting would just add a contradicting row. No server-side rendering, no new dependency. See decision #8. |

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
8. **Minimal UI format (Phase 8)**: a static `ui/index.html` (inline
   CSS/JS, no build step) that calls the existing `GET /suggestions` and
   `POST /feedback` via `fetch()`, served by the same FastAPI app through
   `StaticFiles` (bundled with Starlette, a `fastapi` dependency already —
   no new package) mounted at `/ui`. Chosen over server-rendered HTML
   (would need Jinja2 as a new dependency and would mix HTML-rendering
   into `api/main.py`, which is deliberately JSON-only per its own
   docstring) and over an interactive CLI (would bypass the HTTP API that
   Phase 6 was specifically built to expose instead of only being
   runnable as a local script). Serving the page from the same origin as
   the API means zero CORS configuration. Feedback buttons call
   `POST /feedback` via `fetch()` rather than a plain HTML form, because
   that endpoint returns JSON, not a redirect a form submission could
   navigate to. This phase does not add `GET /feedback` or a
   feedback-history view — decision #7's reasoning for deferring it still
   holds; the UI only needs to show the current week's suggestions and
   let the user react to them, not review past reactions.
9. **Deployment model reconsidered (Phase 9)**: originally planned as a
   public, self-service demo — the idea being that a prospective employer
   could visit a public URL, connect their own Google account, fill in a
   profile, and see the app work end-to-end. Dropped for two independent
   reasons, either one sufficient on its own to rule it out:
   - The OAuth consent screen is in "Testing" status (decision #1), which
     only allows Google accounts explicitly added as test users to
     authenticate at all. An anonymous visitor cannot complete the login —
     not "unlikely to bother", but a hard block from Google itself, no
     matter how the app is hosted.
   - Even with full access and Phase 10's feedback loop already built,
     observing a *learning effect* from a couple of likes/dislikes in one
     short sitting isn't realistic — a visible shift needs sustained real
     usage over time, not a two-minute click-through. This has nothing to
     do with hosting either.

   Revised plan: deploy for genuine personal use, running via
   `docker compose` on the user's own machine. This keeps
   `calendar_module.client`'s existing OAuth flow completely unchanged —
   the process still runs on the same machine where the browser login
   happens, exactly as it does today. A real cloud host (e.g. Fly.io) was
   considered and rejected for now: it would require solving OAuth for a
   headless remote machine (uploading `token.json` as a secret and
   re-uploading it roughly weekly per decision #1's known token-expiry
   trade-off, or pursuing Google's app verification to remove that
   expiry) for a benefit — "always on independent of my own machine" —
   that a single-user personal tool doesn't actually need.

   Remote access was considered and dropped, in two rounds. First idea: a
   `cloudflared` sidecar fronted by Cloudflare Access, giving a real
   HTTPS URL reachable from any device, gated by login. Ruled out once it
   became clear a *named* tunnel's Public Hostname — the feature needed
   for a stable URL with Access in front of it — requires a domain
   registered on Cloudflare's own DNS; free registrars like Freenom
   stopped offering free domains in 2024, so this meant buying one
   (cheap, ~$3-10/year, but still a recurring cost and setup step for one
   user). Fallback idea: Tailscale, a private VPN mesh, free for personal
   use, no domain needed — also dropped, since it still requires
   installing and logging into a client on every device used to reach the
   app, for a benefit (checking suggestions away from this Mac) that
   isn't actually needed here.

   Landed on: local-only. The container binds to `127.0.0.1` (see
   `docker-compose.yml`), so it's reachable only from this same
   machine — Docker here is purely for a consistent, one-command way to
   run it, not for exposing it to anything beyond this Mac. For
   showcasing the project externally (e.g. in a resume), the artifact is
   the repository itself: a README with screenshots of the real running
   app, clean code, and the test suite — not a link a stranger can
   self-serve through.

10. **Hardening: external API error handling (Phase 10, step 1)**:
    `events_module.client.search_events()` and
    `calendar_module.client.get_busy_periods()` now catch a live failure of
    the API they call — `requests.exceptions.RequestException` (connection
    errors, timeouts, non-2xx responses) for Ticketmaster,
    `googleapiclient.errors.HttpError` for Google Calendar — and re-raise
    as `RuntimeError`. Before this, only the "not configured yet" cases
    (missing API key, missing/expired token) were handled; a live outage
    or rate-limit on either external API propagated as an unhandled
    exception, and FastAPI turned that into a raw `500` with a traceback
    instead of the clean `503` every other "can't fulfill this request
    right now" case already gets. Chose to reuse the existing
    `RuntimeError` -> `503` path (`api/main.py`'s `except RuntimeError` in
    `get_suggestions()`) rather than introduce a new exception type or a
    `502` status for this specific case — from the caller's point of view,
    "not configured" and "configured but unavailable right now" both boil
    down to the same thing: retry later, nothing fixable immediately. Keeps
    the change to two `try/except` blocks, no new abstraction.

11. **Hardening: logging (Phase 10, step 2)**: stdlib `logging`, configured
    once via `logging.basicConfig(...)` in `config.py` — that module is
    already imported first by both `uvicorn api.main:app` and every script
    in `scripts/`, so this is the one place a single setup call reaches
    every entry point. Logs to stdout only, no log file: this is a
    personal, single-user app run via `uvicorn --reload` or
    `docker compose up`, and both already surface stdout directly (the
    terminal, or `docker compose logs`) — a log file would need its own
    volume mount in `docker-compose.yml` (the container filesystem is
    ephemeral) and a rotation policy, for a benefit — log history surviving
    a container restart — nothing here actually needs yet. Doesn't
    configure `uvicorn`'s own access logging, which already logs every HTTP
    request by default. Each module gets its own `logger =
    logging.getLogger(__name__)` (standard practice — output is
    attributable to the module that produced it) rather than one shared
    logger. Calls added at real boundaries, not everywhere: pipeline
    entry/exit in `core.suggest_events()` (gap/event/suggestion counts),
    the external-API failure paths added in decision #10 plus the
    pre-existing `RefreshError` case in `calendar_module.client`, and the
    feedback write in `feedback_module.store.record_feedback()`.

12. **Feedback loop (Phase 10, step 3)**: closes the loop `feedback.db` has
    been collecting since Phase 7 but never used — the user explicitly
    wants a real trained model here (not the simpler "boost by matching
    classification" heuristic that was the initial recommendation) for
    portfolio value, and accepted the trade-offs: little data so far, a new
    dependency, added complexity. Design, to keep that choice from becoming
    overengineering:
    - **Model**: `scikit-learn`'s `LogisticRegression`, retrained from
      scratch on every `suggest_events()` call from whatever is currently
      in `feedback.db` — no persisted model file, no versioning, no
      separate training pipeline. With feedback likely staying in the tens
      or low hundreds of rows for a single-user app, retraining takes
      milliseconds; persistence would be complexity with no payoff.
    - **Cold start**: below `MIN_FEEDBACK_FOR_MODEL` labeled examples (or
      without both classes present), the model is skipped entirely and
      ranking falls back to the existing pure cosine-similarity score —
      same spirit as decision #3's honesty about cosine-similarity's
      narrow real-world range: don't trust a model on data too thin to
      support one.
    - **Features, kept minimal on purpose**: the existing `cosine_score`
      (so the content-based signal isn't thrown away, just re-weighted)
      plus the event's classification *segment* (first component of
      `Event.classification`, one-hot) — not the full classification
      string, which is too specific to ever repeat across different real
      events (e.g. "Arts & Theatre, Cultural, Cultural" vs "Arts & Theatre,
      Dance, Dance" share a segment but would never match as full strings).
    - **Step 3.1**: added `classification` to the `feedback` table (the
      only new column needed — `score` already existed) and threaded it
      through `record_feedback()`, `FeedbackRequest` (`api/main.py`), and
      the `POST /feedback` body in `ui/index.html` (the data was already
      available client-side from `GET /suggestions`, just wasn't being sent
      back). No migration path needed — the old `feedback.db` held only
      manual test clicks and was deleted rather than migrated.
    - **Step 3.2 (this commit)**: `feedback_module.store` gained
      `FeedbackRow` + `get_all_feedback()` — an internal read path (still no
      HTTP `GET /feedback`, decision #7 stands). New module
      `classifier_module/feedback_model.py`: `train_feedback_model()`
      returns `None` below `MIN_FEEDBACK_FOR_MODEL` rows or when only one
      class is represented so far (logistic regression can't fit a
      boundary from one class); otherwise returns a `FeedbackModel`
      (the fitted model plus the fixed list of classification segments it
      was trained on, needed so `predict_score()` builds a feature vector
      in the same shape for a new event — including one it's never seen a
      segment for, via an all-zero one-hot block rather than an error).
      Pure logic, no I/O inside the module itself, so it's fully unit
      tested (`tests/test_feedback_model.py`) including a real behavioral
      check (not just "doesn't crash"): trained on synthetic data where
      "Music" is always liked and "Sports" always disliked, it predicts a
      higher score for an unseen Music event than an unseen Sports event
      at the same cosine_score. Wiring this into `core.suggest_events()`
      (calling it once per run, not once per gap — same reasoning as the
      existing "embed once, not per gap" pattern) is step 3.3.

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
| 8 | Minimal UI | Done — static `ui/index.html` + `StaticFiles` at `/ui` (see decision #8) |
| 9 | Deployment (Docker, local-only) + portfolio material | Done — see decision #9; `docker-compose.yml` verified end-to-end, README documents both run paths and carries screenshots |
| 10 | Hardening (error handling, logging, feedback loop) | In progress — steps 1-2 done (decisions #10-11); feedback loop (step 3) in progress: 3.1 (schema) and 3.2 (model, `classifier_module/feedback_model.py`) done, see decision #12; 3.3 (wiring into core.py) next |

Each phase is broken into its own commits as it's implemented; the commit
history is the source of truth for the actual sequence and timing.
