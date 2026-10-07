#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
if [ "${1:-}" != --env-loaded ]; then
    BOOTSTRAP_PYTHON="${VENV_DIR:-$PROJECT_ROOT/.venv}/bin/python"
    if [ ! -x "$BOOTSTRAP_PYTHON" ]; then
        echo "Missing virtual environment: install requirements/base.txt in .venv or set VENV_DIR." >&2
        exit 1
    fi
    exec "$BOOTSTRAP_PYTHON" "$PROJECT_ROOT/jobs/environment.py" \
        bash "$PROJECT_ROOT/scripts/run_processing.sh" --env-loaded "$@"
fi
shift
STAGE="${1:?expected ingest, chunk, tag, or embed}"
shift
case "$STAGE" in ingest|chunk|tag|embed) ;; *) exit 2 ;; esac
VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv}"
if [ "$STAGE" = embed ]; then
    VENV_DIR="${EMBEDDING_VENV_DIR:-${EMBEDDING_ONNX_VENV_DIR:-$PROJECT_ROOT/.venv-embedding-onnx}}"
fi
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Missing virtual environment: $VENV_DIR. See README.md setup instructions." >&2
    exit 1
fi
VENV_DIR="$(cd "$VENV_DIR" && pwd)"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
MODULE=chunking.pipeline
if [ "$STAGE" = ingest ]; then MODULE=ingestion.pipeline; fi
if [ "$STAGE" = tag ]; then MODULE=tagging.pipeline; fi
if [ "$STAGE" = embed ]; then MODULE=embeddings.pipeline; fi
for argument in "$@"; do
    if [ "$argument" = --help ] || [ "$argument" = -h ]; then
        exec "$VENV_DIR/bin/python" -m "$MODULE" "$@"
    fi
done
# Resolve CLI and environment settings before packaging or contacting the cluster.
RESOLVED="$("$VENV_DIR/bin/python" -m jobs.launch_config "$STAGE" "$@")"
IFS=$'\t' read -r SPARK_EXECUTOR_INSTANCES RESOLVED_DRY_RUN DRIVER_MEMORY EXECUTOR_MEMORY EXECUTOR_MEMORY_OVERHEAD <<< "$RESOLVED"
export SPARK_EXECUTOR_INSTANCES
if [ "$RESOLVED_DRY_RUN" = 1 ]; then
    exec "$VENV_DIR/bin/python" -m "$MODULE" "$@"
fi
BUILD_DIR="$PROJECT_ROOT/.build-tmp"
mkdir -p "$BUILD_DIR"
TASK_TMP="$(mktemp -d "$BUILD_DIR/pack-XXXXXX")"
trap 'rm -rf "$TASK_TMP"' EXIT
ZIP="$TASK_TMP/project_code.zip"
zip -qr "$ZIP" ingestion db chunking tagging embeddings jobs -x '*/__pycache__/*' '*.pyc'

if [ "$STAGE" = embed ]; then
    EMBEDDING_SOURCE="${EMBEDDING_MODEL_DIR:-$PROJECT_ROOT/.models/bge-m3-int8}"
    if [ ! -s "$EMBEDDING_SOURCE/onnx/model_int8.onnx" ] || [ ! -s "$EMBEDDING_SOURCE/tokenizer.json" ]; then
        echo "Missing INT8 embedding model or tokenizer in $EMBEDDING_SOURCE. Prepare it with scripts/setup_embedding_onnx_env.sh and scripts/download_quantized_embedding_model.sh." >&2
        exit 1
    fi
    EMBEDDING_SOURCE="$(cd "$EMBEDDING_SOURCE" && pwd)"
    export EMBEDDING_MODEL_DIR="$EMBEDDING_SOURCE"
    MODEL_FINGERPRINT="$(find "$EMBEDDING_SOURCE" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d ' ' -f 1)"
    MODEL_ARCHIVE="$BUILD_DIR/embedding_model-$MODEL_FINGERPRINT.tar.gz"
    if [ ! -f "$MODEL_ARCHIVE" ]; then
        tar -C "$EMBEDDING_SOURCE" -czf "$TASK_TMP/embedding-model.tar.gz" .
        mv "$TASK_TMP/embedding-model.tar.gz" "$MODEL_ARCHIVE"
    fi
    "$VENV_DIR/bin/python" -c 'import numpy, onnxruntime, transformers, pgvector.psycopg2'
fi

# Hash installed distributions as well as declared dependencies and Python.
VENV_FINGERPRINT="$(
    {
        if [ "$STAGE" = ingest ]; then
            cat requirements/base.txt "$VENV_DIR/pyvenv.cfg"
        elif [ "$STAGE" = embed ]; then
            cat requirements/embedding-worker-onnx.txt "$VENV_DIR/pyvenv.cfg"
        else
            cat requirements/base.txt requirements/rag.txt requirements/tagging-groq.txt "$VENV_DIR/pyvenv.cfg"
        fi
        "$VENV_DIR/bin/python" -c 'import importlib.metadata as m, sysconfig; print("\n".join(sorted(d.metadata["Name"] + "==" + d.version for d in m.distributions(path=[sysconfig.get_path("purelib")]))))'
        "$VENV_DIR/bin/python" -c 'import sys; print(sys.version); print(sys.executable)'
    } | sha256sum | cut -d ' ' -f 1
)"
VENV_ARCHIVE="$BUILD_DIR/pyspark_venv-${VENV_FINGERPRINT}.tar.gz"
if [ ! -f "$VENV_ARCHIVE" ]; then
    echo "Packing worker environment..."
    "$VENV_DIR/bin/python" -m venv_pack -p "$VENV_DIR" -o "$TASK_TMP/environment.tar.gz"
    mv "$TASK_TMP/environment.tar.gz" "$VENV_ARCHIVE"
fi
ARCHIVES_SPEC="$VENV_ARCHIVE#environment"
HDFS_APPS_DIR="${HDFS_APPS_DIR:-/user/$USER/apps/spark}"
EXTRA_CONF=()

publish_hdfs() {
    local source="$1" destination="$2" temporary="$2.upload-$(basename "$TASK_TMP")"
    if hdfs dfs -test -e "$destination" 2>/dev/null; then return 0; fi
    hdfs dfs -mkdir -p "$HDFS_APPS_DIR" || return 1
    hdfs dfs -put "$source" "$temporary" || return 1
    if hdfs dfs -mv "$temporary" "$destination"; then return 0; fi
    hdfs dfs -rm -f "$temporary" >/dev/null 2>&1 || true
    hdfs dfs -test -e "$destination"
}

if [ "${USE_HDFS_CACHE:-1}" = 1 ] && hdfs dfs -test -e / >/dev/null 2>&1; then
    VENV_HASH="$(sha256sum "$VENV_ARCHIVE" | cut -d ' ' -f 1)"
    HDFS_VENV="$HDFS_APPS_DIR/pyspark_venv-$VENV_HASH.tar.gz"
    if publish_hdfs "$VENV_ARCHIVE" "$HDFS_VENV"; then
        ARCHIVES_SPEC="hdfs://$HDFS_VENV#environment"
    fi
    if [ "$STAGE" = embed ]; then
        HDFS_MODEL="$HDFS_APPS_DIR/embedding_model-$MODEL_FINGERPRINT.tar.gz"
        if publish_hdfs "$MODEL_ARCHIVE" "$HDFS_MODEL"; then
            MODEL_ARCHIVE_SPEC="hdfs://$HDFS_MODEL#embedding-model"
        else
            MODEL_ARCHIVE_SPEC="$MODEL_ARCHIVE#embedding-model"
        fi
    fi
    : "${SPARK_HOME:?Set SPARK_HOME to the cluster Spark installation}"
    JARS_HASH="$(find "$SPARK_HOME/jars" -maxdepth 1 -name '*.jar' -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d ' ' -f 1)"
    JARS_ARCHIVE="$BUILD_DIR/spark-libs-$JARS_HASH.zip"
    if [ ! -f "$JARS_ARCHIVE" ]; then
        (cd "$SPARK_HOME/jars" && zip -qr "$TASK_TMP/spark-libs.zip" .)
        mv "$TASK_TMP/spark-libs.zip" "$JARS_ARCHIVE"
    fi
    HDFS_JARS="$HDFS_APPS_DIR/spark-libs-$JARS_HASH.zip"
    if publish_hdfs "$JARS_ARCHIVE" "$HDFS_JARS"; then
        EXTRA_CONF+=(--conf "spark.yarn.archive=hdfs://$HDFS_JARS")
    fi
fi
if [ "$STAGE" = embed ]; then
    MODEL_ARCHIVE_SPEC="${MODEL_ARCHIVE_SPEC:-$MODEL_ARCHIVE#embedding-model}"
    ARCHIVES_SPEC="$ARCHIVES_SPEC,$MODEL_ARCHIVE_SPEC"
fi
export PYSPARK_DRIVER_PYTHON="$VENV_DIR/bin/python"
export PYSPARK_PYTHON="./environment/bin/python"
if [ "$STAGE" = ingest ]; then
    SPARK_SUBMIT=spark-submit
else
    SPARK_SUBMIT="${SPARK_HOME:?Set SPARK_HOME}/bin/spark-submit"
    EXTRA_CONF+=(--conf spark.speculation=false --conf spark.task.maxFailures=1)
fi
"$SPARK_SUBMIT" \
    --master yarn --deploy-mode client \
    --driver-memory "$DRIVER_MEMORY" \
    --executor-memory "$EXECUTOR_MEMORY" \
    --conf "spark.executor.memoryOverhead=$EXECUTOR_MEMORY_OVERHEAD" \
    --conf spark.executor.cores=1 \
    --conf "spark.executor.instances=$SPARK_EXECUTOR_INSTANCES" \
    --conf spark.dynamicAllocation.enabled=false \
    --conf spark.driver.maxResultSize=64m \
    --conf spark.executorEnv.RAYON_NUM_THREADS=1 \
    --conf spark.executorEnv.OMP_NUM_THREADS=1 \
    --conf spark.executorEnv.OPENBLAS_NUM_THREADS=1 \
    --conf "spark.pyspark.driver.python=$VENV_DIR/bin/python" \
    --conf "spark.pyspark.python=$PYSPARK_PYTHON" \
    "${EXTRA_CONF[@]}" --archives "$ARCHIVES_SPEC" --py-files "$ZIP" "scripts/${STAGE}.py" "$@"
