#!/usr/bin/env bash
# Export article and enrichment tables to CSV, then copy to the HGFS share.
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

echo "Exporting article and enrichment tables to $CSV_DIR (db: $PGHOST:$PGPORT/$PGDATABASE as $PGUSER)"

TABLES=(websites authors pages metadata content chunk_materializations article_chunks chunk_analyses chunk_embeddings)
ORDER_BY=(
  'id' 'id' 'id' 'page_id' 'page_id'
  'page_id, chunking_version'
  'page_id, chunking_version, chunk_index'
  'page_id, chunking_version, chunk_index, backend, model, analysis_version'
  'page_id, chunking_version, chunk_index, embedding_model, embedding_version'
)
STAGING_DIR="$(mktemp -d "$CSV_DIR/.export-XXXXXX")"
trap 'rm -rf -- "$STAGING_DIR"' EXIT
CSV_FILES=()
for i in "${!TABLES[@]}"; do
  table="${TABLES[$i]}"
  psql -X -q -v ON_ERROR_STOP=1 \
    -c "COPY (SELECT * FROM $table ORDER BY ${ORDER_BY[$i]}) TO STDOUT WITH CSV HEADER" \
    > "$STAGING_DIR/$table.csv"
done
for table in "${TABLES[@]}"; do
  mv -f "$STAGING_DIR/$table.csv" "$CSV_DIR/$table.csv"
  CSV_FILES+=("$CSV_DIR/$table.csv")
done

echo "Row counts:"
for table in "${TABLES[@]}"; do
  printf '  %-23s %s rows\n' "$table" "$(psql -X -tA -v ON_ERROR_STOP=1 -c "SELECT count(*) FROM $table;")"
done
ls -lh "$CSV_DIR"

mkdir -p "$DEST_DIR"
cp -f "${CSV_FILES[@]}" "$DEST_DIR"/
echo "Copied ${#TABLES[@]} CSVs to $DEST_DIR:"
ls -lh "$DEST_DIR"
