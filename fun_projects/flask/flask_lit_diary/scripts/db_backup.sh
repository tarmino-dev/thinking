#!/usr/bin/env bash
#
# Back up a PostgreSQL database into a timestamped custom-format dump.
#
# Intended for the Render production database, but works against any PostgreSQL
# instance reachable from this machine. Run it locally against the database's
# External Database URL (from the Render dashboard).
#
# Setup & run (do the steps in order; do NOT type the URL on the command line):
#
#   1. Add the source database's External Database URL to your shell profile
#      (e.g. ~/.zshrc). Keeping it in a file rather than typing it inline means
#      it is never recorded in your shell history:
#
#          export SOURCE_DATABASE_URL="postgres://USER:PASS@HOST:PORT/DBNAME"
#
#   2. Reload the profile so the variable is available in the current shell
#      (or just open a new terminal):
#
#          source ~/.zshrc
#
#   3. Run the script (no arguments, no credentials on the command line):
#
#          ./scripts/db_backup.sh
#
#
# Output: backups/posts_YYYYMMDD_HHMMSS.dump (restore it with scripts/db_restore.sh).

set -euo pipefail

if [[ -z "${SOURCE_DATABASE_URL:-}" ]]; then
  echo "Error: SOURCE_DATABASE_URL is not set." >&2
  echo "Set it in your shell profile (e.g. ~/.zshrc), reload it, then run: $0" >&2
  echo "See the header of this script for the full procedure." >&2
  exit 1
fi

# Normalize a SQLAlchemy-style URL (postgresql+psycopg2://) to a libpq URL.
url="$SOURCE_DATABASE_URL"
url="${url/+psycopg2:/:}"
url="${url/+psycopg:/:}"

# Resolve paths relative to the repository root (parent of this script's dir).
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
backup_dir="$repo_root/backups"
mkdir -p "$backup_dir"

timestamp="$(date +%Y%m%d_%H%M%S)"
outfile="$backup_dir/posts_${timestamp}.dump"

echo "Creating backup..."
pg_dump --format=custom --file="$outfile" "$url"

if [[ ! -s "$outfile" ]]; then
  echo "Error: backup file was not created or is empty: $outfile" >&2
  exit 1
fi

size="$(du -h "$outfile" | cut -f1)"
echo "Backup complete: $outfile ($size)"
