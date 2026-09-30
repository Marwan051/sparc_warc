import importlib.util
import unittest
from unittest.mock import Mock, patch

AVAILABLE = importlib.util.find_spec('langchain_core') is not None and importlib.util.find_spec('langchain_text_splitters') is not None


@unittest.skipUnless(AVAILABLE, 'install requirements-rag.txt for optional RAG tests')
class RagTests(unittest.TestCase):
    def test_incremental_fetch_and_early_close(self):
        import rag_loader as rag
        consumed = []
        def rows():
            for i in range(100):
                consumed.append(i)
                yield (i, 'text', 'https://example.com', 'Title','example.com','A','en',None,None,str(i))
        class Cursor:
            def __iter__(self): return rows()
            execute = Mock()
            close = Mock()
        cursor = Cursor()
        conn = Mock(); conn.cursor.return_value = cursor
        with patch.object(rag, 'get_connection', return_value=conn):
            stream = rag.iter_documents()
            self.assertEqual(consumed, [])
            self.assertEqual(next(stream).page_content, 'text')
            self.assertEqual(consumed, [0])
            stream.close()
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_eager_loader_requires_limit(self):
        import rag_loader as rag
        with patch.dict('os.environ', {}, clear=True), self.assertRaises(ValueError):
            rag.load_documents_distributed()
