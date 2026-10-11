"""Ask one grounded question against the stored news vectors."""

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobs.environment import load_environment


def _print_evidence(evidence):
    print("\nRetrieved evidence:")
    if not evidence:
        print("(none)")
        return
    for index, item in enumerate(evidence, 1):
        print(f"\n[{index}] chunks={','.join(item.chunk_ids)} "
              f"cosine={item.similarity:.6f} queries={','.join(item.query_ids)}")
        for source in item.sources:
            print(f"Source: {source.title} | {source.url}")
        print(item.text)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ask the local news RAG agent")
    parser.add_argument("question", help="question to answer from the vector database")
    args = parser.parse_args(argv)
    load_environment(ROOT / ".env")

    from retrieval import answer
    result = asyncio.run(answer(args.question))
    print(result.answer)
    if result.sources:
        print("\nSources:")
        for source in result.sources:
            print(f"- {source.title} ({source.url})")
    _print_evidence(result.evidence)
    return 0 if result.sufficient else 1


if __name__ == "__main__":
    raise SystemExit(main())
