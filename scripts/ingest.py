"""Spark submission entry point; application modules arrive via --py-files."""

from ingestion.pipeline import main

if __name__ == "__main__":
    main()
