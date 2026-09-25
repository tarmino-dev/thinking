"""Manual check: run the full orchestrator pipeline end-to-end.

This is not an automated test — it's a script you run by hand to see the
final product: real calendar gaps, filled with real nearby events, ranked
against your real interests via TinyBERT. Run it from the project root:

    PYTHONPATH=. python3 scripts/check_suggestions.py
"""

from core import suggest_events


def main() -> None:
    suggestions = suggest_events()

    for gap, ranked in suggestions:
        print(f"\n{gap.start:%d.%m %H:%M}–{gap.end:%H:%M}")
        if not ranked:
            print("  (no fitting events)")
            continue
        for ranked_event in ranked:
            event = ranked_event.event
            venue = f" @ {event.venue_name}" if event.venue_name else ""
            print(f"  {ranked_event.score:.3f}  {event.start:%d.%m %H:%M}  {event.name}{venue}")


if __name__ == "__main__":
    main()
