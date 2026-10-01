"""Repeat near-budget worker chunks and report RSS after warmup."""
import gc
import json
import resource
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_ingestion import make_warc, task, Response
from ingestion import pipeline as job

body = ('<html><body><p>' + 'The government published a report on public transport and the local economy. ' * 4000 + '</p></body></html>').encode()
data, _ = make_warc(20, payload=body)
peaks, sizes = [], []
for i in range(20):
    with patch.object(job.urllib.request, 'urlopen', return_value=Response(data)):
        result = job.process_file_chunk(task(candidate_limit=100, use_trafilatura=False))
    assert result['error'] is None, result['error']
    assert result['stats']['result_bytes'] <= 4194304
    sizes.append(result['stats']['result_bytes'])
    del result
    gc.collect()
    peaks.append(round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2))
assert max(peaks[5:])-peaks[5] < 64, peaks
print(json.dumps(dict(chunks=20, payload_bytes=sizes, peak_rss_mib=peaks)))
