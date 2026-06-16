#!/usr/bin/env bash
#
# Restore a custom-format dump (made by scripts/db_backup.sh) into a PostgreSQL
# database.
#
# This variant targets a freshly created, empty database (e.g. a new Render
# PostgreSQL instance). Run it locally against the target database's External
# Database URL. For the same major version as the source (Render: PostgreSQL 18).
#
# Setup & run (do the steps in order; do NOT type the URL on the command line):
#
#   1. Add the target database's External Database URL to your shell profile
#      (e.g. ~/.zshrc). Keeping it in a file rather than typing it inline means
#      it is never recorded in your shell history:
#
#          export TARGET_DATABASE_URL="postgres://USER:PASS@HOST:PORT/DBNAME"
#
#   2. Reload the profile so the variable is available in the current shell
#      (or just open a new terminal):
#
#          source ~/.zshrc
#
#   3. Run the script, passing the dump file to restore:
#
#          ./scripts/db_restore.sh backups/posts_YYYYMMDD_HHMMSS.dump
#
#      Add the -y flag to skip the confirmation prompt (for non-interactive use):
#
#          ./scripts/db_restore.sh -y backups/posts_YYYYMMDD_HHMMSS.dump
#

set -euo pipefail

assume_yes=false
if [[ "${1:-}" == "-y" ]]; then
  assume_yes=true
  shift
fi

backup_file="${1:-}"

if [[ -z "${TARGET_DATABASE_URL:-}" || -z "$backup_file" ]]; then
  echo "Error: TARGET_DATABASE_URL must be set and a backup file must be given." >&2
  echo "Set TARGET_DATABASE_URL in your shell profile (e.g. ~/.zshrc), reload it," >&2
  echo "then run: $0 [-y] BACKUP_FILE" >&2
  echo "See the header of this script for the full procedure." >&2
  exit 1
fi

if [[ ! -s "$backup_file" ]]; then
  echo "Error: backup file not found or empty: $backup_file" >&2
  exit 1
fi

# Normalize a SQLAlchemy-style URL (postgresql+psycopg2://) to a libpq URL.
url="$TARGET_DATABASE_URL"
url="${url/+psycopg2:/:}"
url="${url/+psycopg:/:}"

# Derive a credential-free label (everything after the last '@') for display.
target_label="${url##*@}"

if [[ "$assume_yes" != true ]]; then
  echo "About to restore '$backup_file' into: $target_label"
  read -r -p "This will write into the target database. Continue? [y/N] " reply
  if [[ "$reply" != "y" && "$reply" != "Y" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

echo "Restoring..."
pg_restore --no-owner --no-privileges --single-transaction --dbname="$url" "$backup_file"

echo "Restore complete into: $target_label"
