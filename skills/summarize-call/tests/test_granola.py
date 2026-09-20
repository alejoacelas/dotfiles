import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


script = Path(__file__).resolve().parents[1] / 'scripts/granola.py'
spec = importlib.util.spec_from_file_location('granola', script)
granola = importlib.util.module_from_spec(spec)
spec.loader.exec_module(granola)


class GranolaTests(unittest.TestCase):
    def test_missing_key_stops_before_network_or_desktop_access(self):
        for action in [granola.check_recent, granola.list_meetings,
                       lambda: granola.get_transcript('not_test'), granola.get_recent_transcript]:
            with self.subTest(action=action), patch.object(granola, '_read_api_key', return_value=None), \
                    patch.object(granola.subprocess, 'run') as request, \
                    contextlib.redirect_stderr(io.StringIO()) as error:
                with self.assertRaises(SystemExit) as raised:
                    action()
                self.assertEqual(raised.exception.code, 1)
                self.assertIn('GRANOLA_API_KEY', error.getvalue())
                request.assert_not_called()

    def test_public_pagination_and_transcript_format(self):
        responses = [
            {'notes': [{'id': 'a', 'updated_at': '2026-01-01'},
                       {'id': 'b', 'updated_at': '2026-01-03'}], 'hasMore': True, 'cursor': 'next'},
            {'notes': [{'id': 'c', 'updated_at': '2026-01-02'}], 'hasMore': False},
            {'id': 'b', 'title': 'Example', 'updated_at': '2026-01-03', 'transcript': [
                {'start_time': '03', 'text': 'Reply', 'speaker': {'source': 'speaker'}},
                {'start_time': '01', 'text': 'Hello', 'speaker': {'source': 'microphone'}},
                {'start_time': '02', 'text': 'there', 'speaker': {'source': 'microphone'}},
            ]},
        ]
        replies = [subprocess.CompletedProcess([], 0, json.dumps(r), '') for r in responses]
        with patch.object(granola, '_read_api_key', return_value='test-key'), \
                patch.object(granola.subprocess, 'run', side_effect=replies) as request:
            self.assertEqual([d['id'] for d in granola.get_recent_documents(3)], ['b', 'c', 'a'])
            self.assertEqual(granola.build_transcript('b'), (
                '# Example\nDate: 2026-01-03\n\n**Me**: Hello there\n\n**Other**: Reply',
                'Example', '2026-01-03'))
            self.assertIn('cursor=next', request.call_args_list[1].args[0])
            for call in request.call_args_list:
                self.assertTrue(any(arg.startswith('https://public-api.granola.ai/v1/')
                                    for arg in call.args[0]))

    def test_empty_transcript_is_an_error(self):
        with patch.object(granola, 'public_get', return_value={'id': 'empty', 'transcript': []}), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                granola.build_transcript('empty')
