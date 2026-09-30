"""FastWARC parsing with bounded payloads and validated gzip transport."""

import zlib
from fastwarc.warc import ArchiveIterator, WarcRecordType


class ValidatedGzipStream:
    """Validate CRC/trailers with bounded scratch space as FastWARC reads.

    FastWARC can return a partial final record on a truncated gzip stream.
    Checking the outer gzip stream prevents that from becoming a saved EOF.
    """
    def __init__(self, source, expected_bytes=None):
        self.source = source
        self.expected_bytes = expected_bytes
        self.bytes_read = 0
        self.decoder = None
        self.at_boundary = True

    def tell(self):
        return self.bytes_read

    def read(self, size=65536):
        if size == 0:
            return b""
        data = self.source.read(min(size if size >= 0 else 65536, 65536))
        self.bytes_read += len(data)
        if not data:
            if not self.at_boundary:
                raise IOError("truncated gzip member")
            if self.expected_bytes is not None and self.bytes_read != self.expected_bytes:
                raise IOError("HTTP body length differs from Content-Length")
            return b""
        pending = data
        while pending:
            if self.at_boundary:
                self.decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                self.at_boundary = False
            try:
                self.decoder.decompress(pending, 65536)
            except zlib.error as error:
                raise IOError(f"invalid gzip member: {error}") from error
            if self.decoder.eof:
                pending = self.decoder.unused_data
                self.at_boundary = True
            else:
                pending = self.decoder.unconsumed_tail
        return data


def parse_warc_records_streaming(stream, max_html_bytes=2 * 1024 * 1024, base_offset=0):
    """Yield every record boundary, including records that cannot be articles.

    HTTP content/transfer decoding is streamed by FastWARC. Read at most the
    decoded HTML limit plus one byte before rejecting an oversized payload.
    Transport validation is supplied by the caller's ValidatedGzipStream.
    """
    iterator = ArchiveIterator(
        stream, parse_http=True, auto_decode="all", max_header_len=64 * 1024,
        stream_detect=True, buffer_size=64 * 1024, fsspec_args=False,
    )
    for record in iterator:
        start_offset = base_offset + record.stream_pos
        content_type = (record.http_content_type or "").lower()
        if record.record_type != WarcRecordType.response or (
            "text/html" not in content_type and "application/xhtml" not in content_type
        ):
            yield {"skip": "non_html", "start_offset": start_offset}
            continue
        payload = record.reader.read(max_html_bytes + 1)
        if len(payload) > max_html_bytes:
            yield {"skip": "oversized_html", "start_offset": start_offset}
            continue
        yield {
            "url": record.headers.get("WARC-Target-URI") or "",
            "warc_date": record.headers.get("WARC-Date"),
            "content_type": content_type, "charset": record.http_charset,
            "record_id": record.record_id or record.headers.get("WARC-Record-ID") or "",
            "raw_bytes": payload, "start_offset": start_offset,
        }


def parse_warc_stream_fastwarc(stream, **kwargs):
    yield from parse_warc_records_streaming(stream, **kwargs)
