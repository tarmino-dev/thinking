# Architecture

## Overview

Calendar Gap Filler is a personal, single-user assistant that finds empty time
slots in a Google Calendar and suggests locally relevant events to fill them,
ranked against the user's interest profile by a lightweight ML model.

## Current status

Calendar Module (Phase 1) is complete: `calendar_module/client.py` reads
busy periods from Google Calendar, `calendar_module/gaps.py` computes free
slots, both covered by a manual e2e check and unit tests. Event Source
Module (Phase 2) is in progress: environment/config is set up and
`events_module/client.py` fetches and normalizes events from the
Ticketmaster Discovery API; unit tests and a manual e2e check are next.
This document describes the target architecture the code is growing into,
module by module, per the roadmap below, and is updated as each module is
actually built.

## Modules (planned)

Flat, package-per-concern structure. No service/repository/factory layers —
each module has one clear responsibility, and a thin orchestrator wires them
together.

| Module | Responsibility | Notes |
|---|---|---|
| `calendar_module/` | Reads the user's Google Calendar (read-only) and computes free time slots ("gaps"). | Split into `client.py` (Google Calendar API access) and `gaps.py` (pure gap-finding logic, no I/O, easy to unit test). |
| `events_module/` | Fetches candidate local events. | Uses the Ticketmaster Discovery API; normalizes results into a common `Event` shape. `Event.duration_minutes` is often `None` — Ticketmaster frequently doesn't provide an event's end time. |
| `profile_module/` | Holds the user's interest profile. | Simple in-memory structure at first; no database yet. |
| `classifier_module/` | Ranks candidate events against the user's interest profile. | TinyBERT embeddings via `sentence-transformers` (`paraphrase-TinyBERT-L6-v2`), ranked by cosine similarity, filtered by gap duration. |
| `orchestrator` (`core.py`) | Single composition point: gaps -> candidate events -> ranked suggestions. | Deliberately not a separate "service layer". |
| `api/` | Exposes the orchestrator over HTTP. | FastAPI. |
| Persistence | Stores cached events, the interest profile, feedback. | SQLite first; introduced once there is real data to store, not needed for the first working end-to-end version. |

## Key architectural decisions

1. **Calendar integration**: Google Calendar API via OAuth2 (Installed App
   flow), scope `calendar.readonly`. Single-user; the app only reads and
   suggests, it never writes to the calendar. Chosen over a secret `.ics`
   feed URL because the product needs near-real-time availability, which the
   `.ics` export does not reliably provide. The official API is also the
   standard, well-supported path and leaves room to add multi-user OAuth
   later without redesigning this module.
2. **Event source**: Ticketmaster Discovery API (free tier, purpose-built for
   event discovery) over Eventbrite (organizer/ticketing focused, not
   discovery focused) and scraping (fragile, legally murky, unnecessary
   complexity for an MVP).
3. **ML ranking**: `sentence-transformers` with a pretrained TinyBERT
   checkpoint (`paraphrase-TinyBERT-L6-v2`) for sentence embeddings, ranked
   by cosine similarity against the user's interest profile. No fine-tuning
   at this stage — revisit only if off-the-shelf ranking quality proves
   insufficient.
4. **Web framework**: FastAPI — typed, low-boilerplate, built-in docs,
   async-friendly for outbound calls to the event source API.
5. **Storage**: SQLite for the MVP; migration to Postgres deferred to the
   deployment phase.
6. **Event search geolocation**: `latlong` + `radius` query params on the
   Ticketmaster Discovery API, over `postalCode` (format varies too much
   between countries) or `geoPoint` (Ticketmaster's newer, non-deprecated
   option, but requires geohash-encoding the user's coordinates — an extra
   dependency for no real benefit at our scale). Risk: `latlong` is marked
   deprecated in Ticketmaster's docs and could be removed in a future API
   version, at which point we'd need to switch to `geoPoint`.

## Roadmap (high level)

| # | Phase | Status |
|---|---|---|
| 1 | Calendar Module | Done |
| 2 | Event Source Module (Ticketmaster integration) | In progress — env/config and `client.py` done; unit tests and manual e2e check next |
| 3 | Profile Module | Not started |
| 4 | ML Ranking Module (TinyBERT embeddings) | Not started |
| 5 | Orchestrator | Not started |
| 6 | API Layer (FastAPI) | Not started |
| 7 | Persistence (SQLite) | Not started — `docs/er_diagram.mermaid` gets its first real content here, once the actual tables (profile, cached events, feedback) are designed |
| 8 | Minimal UI | Not started — format tbd |
| 9 | Deployment (Docker + hosting, public URL) | Not started |
| 10 | Hardening (error handling, logging, feedback loop) | Not started |

Each phase is broken into its own commits as it's implemented; the commit
history is the source of truth for the actual sequence and timing.
