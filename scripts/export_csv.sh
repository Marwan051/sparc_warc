#!/usr/bin/env bash
# Export important article tables to CSV, then copy to the HGFS share.
# Usage:
#   export PGHOST=... PGPORT=... PGDATABASE=... PGUSER=... PGPASSWORD=...
#   ./scripts/export_csv.sh [csv_dir] [dest_dir]
# Defaults: csv_dir=<project>/exports  dest_dir=/mnt/hgfs/copy_path/warcdb_csv
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CSV_DIR="${1:-$PROJECT_ROOT/exports}"
DEST_DIR="${2:-/mnt/hgfs/copy_path/warcdb_csv}"
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGDATABASE="${PGDATABASE:-warcdb}"
export PGUSER="${PGUSER:-warc_user}"
export PGPASSWORD="${PGPASSWORD:-password}"
mkdir -p "$CSV_DIR"

echo "Exporting article tables to $CSV_DIR (db: $PGHOST:$PGPORT/$PGDATABASE as $PGUSER)"

psql -v ON_ERROR_STOP=1 -c "\copy (SELECT * FROM websites ORDER BY id) TO '$CSV_DIR/websites.csv' WITH CSV HEADER"
psql -v ON_ERROR_STOP=1 -c "\copy (SELECT * FROM authors ORDER BY id) TO '$CSV_DIR/authors.csv' WITH CSV HEADER"
psql -v ON_ERROR_STOP=1 -c "\copy (SELECT * FROM pages ORDER BY id) TO '$CSV_DIR/pages.csv' WITH CSV HEADER"
psql -v ON_ERROR_STOP=1 -c "\copy (SELECT * FROM metadata ORDER BY page_id) TO '$CSV_DIR/metadata.csv' WITH CSV HEADER"
psql -v ON_ERROR_STOP=1 -c "\copy (SELECT * FROM content ORDER BY page_id) TO '$CSV_DIR/content.csv' WITH CSV HEADER"

echo "Row counts:"
for t in websites authors pages metadata content; do
  printf '  %-8s %s rows\n' "$t" "$(psql -tA -v ON_ERROR_STOP=1 -c "SELECT count(*) FROM $t;")"
done
ls -lh "$CSV_DIR"

mkdir -p "$DEST_DIR"
cp -f "$CSV_DIR"/websites.csv "$CSV_DIR"/authors.csv "$CSV_DIR"/pages.csv \
      "$CSV_DIR"/metadata.csv "$CSV_DIR"/content.csv "$DEST_DIR"/
echo "Copied 5 CSVs to $DEST_DIR:"
ls -lh "$DEST_DIR"
