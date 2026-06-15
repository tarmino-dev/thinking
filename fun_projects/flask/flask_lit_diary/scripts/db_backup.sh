#!/usr/bin/env bash
#
# Back up a PostgreSQL database into a timestamped custom-format dump.
#
# Intended for the Render production database, but works against any PostgreSQL
# instance reachable from this machine. Run it locally against the database's
# External Database URL (from the Render dashboard).
#
# Usage:
#   SOURCE_DATABASE_URL="postgres://USER:PASS@HOST:PORT/DBNAME" ./scripts/db_backup.sh
#
# The connection URL is read from the SOURCE_DATABASE_URL environment variable
# (not a command-line argument) so credentials never leak into shell history or
# process listings. The URL itself is never printed.
#
# Output: backups/posts_YYYYMMDD_HHMMSS.dump (restore it with scripts/db_restore.sh).

set -euo pipefail

if [[ -z "${SOURCE_DATABASE_URL:-}" ]]; then
  echo "Error: SOURCE_DATABASE_URL is not set." >&2
  echo "Usage: SOURCE_DATABASE_URL=postgres://USER:PASS@HOST:PORT/DBNAME $0" >&2
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
