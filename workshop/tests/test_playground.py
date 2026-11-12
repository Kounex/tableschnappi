"""Execute the notebook's real agent against local model/MCP protocol stubs.

Uses real LangGraph, ChatOpenAI and MLflow storage; no cluster or provider key.
"""
import json
import os
from pathlib import Path
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import unittest
from unittest.mock import patch

import mlflow

WORKSHOP = Path(__file__).resolve().parents[1]


class StubHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if self.path == '/v1/chat/completions':
            self.server.model_calls += 1
            use_tool = body.get('tools') and (self.server.loop or body['messages'][-1]['role'] == 'user')
            message = {'role': 'assistant', 'content': 'Vegetarian udon, from the menu.'}
            if use_tool:
                message = {'role': 'assistant', 'content': None, 'tool_calls': [{
                    'id': f'call-{self.server.model_calls}', 'type': 'function',
                    'function': {'name': self.server.tool_name,
                                 'arguments': json.dumps({'slug': 'sakura'})},
                }]}
            payload = {'id': 'chat-test', 'object': 'chat.completion', 'created': 1,
                       'model': 'local-test-model', 'choices': [{'index': 0, 'message': message,
                       'finish_reason': 'tool_calls' if use_tool else 'stop'}],
                       'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}}
            content_type = 'application/json'
            data = json.dumps(payload)
        else:
            self.server.mcp_methods.append(body['method'])
            self.server.roles.append(self.headers.get('X-TableSchnappi-Role'))
            if body['method'] == 'tools/list':
                result = {'tools': [{'name': name, 'description': name,
                          'inputSchema': {'type': 'object', 'properties': {'slug': {'type': 'string'}},
                                          'required': ['slug']}}
                         for name in ['get_menu', 'get_wait_time', 'make_reservation']]}
            else:
                result = {'content': [{'type': 'text', 'text': 'Vegetarian udon'}],
                          'isError': self.server.tool_error}
            payload = {'jsonrpc': '2.0', 'id': body['id'], 'result': result}
            if self.server.sse:
                # Exercise multiline SSE data framing as well as ordinary JSON.
                data = 'event: message\n' + '\n'.join('data: ' + line for line in json.dumps(payload, indent=1).splitlines()) + '\n\n'
                content_type = 'text/event-stream'
            else:
                data, content_type = json.dumps(payload), 'application/json'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(data.encode())


class PlaygroundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), StubHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.environment = patch.dict(os.environ, {
            'MLFLOW_TRACKING_URI': f'sqlite:///{cls.directory.name}/tracking.db',
            'MLFLOW_TRACKING_AUTH': '', 'MLFLOW_WORKSPACE': 'default',
            'MODEL_BASE_URL': url + '/v1', 'MODEL_NAME': 'local-test-model',
            'MODEL_EXTRA_BODY': 'false', 'OPENAI_API_KEY': 'local-test-only',
            'MCP_URL': url + '/mcp', 'RESTAURANT_API_URL': url, 'MLFLOW_ENABLE_ASYNC_TRACE_LOGGING': 'false',
        })
        cls.environment.start()
        mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
        import sys
        sys.path.insert(0, str(WORKSHOP))
        cls.scope = {}
        notebook = json.loads((WORKSHOP / 'agent-playground.ipynb').read_text())
        for index, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                if cell['outputs'] or cell['execution_count'] is not None:
                    raise AssertionError('Do not publish executed notebook outputs')
                exec(compile(''.join(cell['source']), f'notebook-cell-{index}', 'exec'), cls.scope)
        cls.experiment = mlflow.get_experiment_by_name('restaurant-agent-playground').experiment_id

    @classmethod
    def tearDownClass(cls):
        mlflow.langchain.autolog(disable=True)
        mlflow.flush_trace_async_logging()
        cls.server.shutdown()
        cls.server.server_close()
        cls.environment.stop()
        cls.directory.cleanup()

    def setUp(self):
        self.scope.update(AUTOLOG=True, MANUAL_SPANS=True, USE_MCP=True, MAX_MODEL_CALLS=3,
                          LABEL=self.id())
        self.server.mcp_methods = []
        self.server.roles = []
        self.server.model_calls = 0
        self.server.tool_name = 'get_menu'
        self.server.loop = False
        self.server.sse = False
        self.server.tool_error = False

    def run_agent(self):
        return self.scope['run_agent']('Check the vegetarian menu at Sakura.')

    def spans(self, result):
        self.assertIsNotNone(result['trace_id'])
        trace = mlflow.get_trace(result['trace_id'])
        self.assertEqual(trace.info.tags['playground.label'], self.id())
        return trace.data.spans

    def test_both_tracing_modes_nest_manual_and_model_spans(self):
        self.server.sse = True
        result = self.run_agent()
        spans = self.spans(result)
        names = {span.name for span in spans}
        self.assertEqual(result['tools'], ['get_menu'])
        self.assertEqual(result['model_calls'], 2)
        self.assertTrue({'playground.turn', 'mcp.get_menu', 'format_answer'} <= names)
        self.assertTrue(any(span.span_type in ('LLM', 'CHAT_MODEL') for span in spans))
        self.assertEqual(sum(span.parent_id is None for span in spans), 1)
        self.assertEqual(set(self.server.roles), {'readonly'})

    def test_autolog_only_keeps_model_spans_without_custom_boundaries(self):
        self.scope['MANUAL_SPANS'] = False
        spans = self.spans(self.run_agent())
        self.assertTrue(any(span.span_type in ('LLM', 'CHAT_MODEL') for span in spans))
        self.assertFalse({'playground.turn', 'mcp.get_menu', 'format_answer'} & {s.name for s in spans})

    def test_manual_only_has_no_framework_model_spans(self):
        self.scope['AUTOLOG'] = False
        spans = self.spans(self.run_agent())
        self.assertEqual({s.name for s in spans}, {'playground.turn', 'mcp.get_menu', 'format_answer'})

    def test_disabling_tracing_after_enabling_does_not_report_stale_trace(self):
        self.run_agent()
        before = len(mlflow.search_traces(experiment_ids=[self.experiment], return_type='list'))
        self.scope.update(AUTOLOG=False, MANUAL_SPANS=False)
        result = self.run_agent()
        self.assertEqual(result['tools'], ['get_menu'])
        self.assertIsNone(result['trace_id'])
        self.assertEqual(len(mlflow.search_traces(experiment_ids=[self.experiment], return_type='list')), before)

    def test_mcp_off_makes_no_discovery_or_tool_requests(self):
        self.scope['USE_MCP'] = False
        result = self.run_agent()
        self.assertEqual(result['tools'], [])
        self.assertEqual(result['model_calls'], 1)
        self.assertEqual(self.server.mcp_methods, [])
        self.assertNotIn('mcp.get_menu', {s.name for s in self.spans(result)})

    def test_unoffered_mutation_tool_is_rejected_without_execution(self):
        self.server.tool_name = 'make_reservation'
        with self.assertRaisesRegex(ValueError, 'Tool was not offered'):
            self.run_agent()
        self.assertEqual(self.server.mcp_methods, ['tools/list'])

    def test_tool_failure_is_not_logged_as_success(self):
        self.server.tool_error = True
        with self.assertRaisesRegex(RuntimeError, 'MCP tool failed'):
            self.run_agent()
        mlflow.flush_trace_async_logging()
        spans = mlflow.get_trace(mlflow.get_last_active_trace_id()).data.spans
        failed = next(span for span in spans if span.name == 'mcp.get_menu')
        self.assertEqual(failed.status.status_code.name, 'ERROR')

    def test_repeated_tool_requests_stop_at_model_limit(self):
        self.server.loop = True
        self.scope['MAX_MODEL_CALLS'] = 2
        with self.assertRaisesRegex(RuntimeError, 'Model-call limit reached'):
            self.run_agent()
        self.assertEqual(self.server.model_calls, 2)
        self.assertEqual(self.server.mcp_methods.count('tools/call'), 1)


if __name__ == '__main__':
    unittest.main()
