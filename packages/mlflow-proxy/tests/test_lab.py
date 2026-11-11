"""Run with the assistant's pinned requirements: python -m unittest discover -s packages/mlflow-proxy/tests."""
import importlib.util
import os
from pathlib import Path
import types
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, local
import unittest
from unittest.mock import patch, Mock

os.environ.update(MLFLOW_TRACKING_URI='', GUARDRAILS_ENABLED='false', VLLM_URL='http://model.example.com/v1', VLLM_MODEL='test-model')
spec = importlib.util.spec_from_file_location('assistant_app', Path(__file__).parents[1] / 'app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage


class LabTests(unittest.TestCase):
    def test_concurrent_turns_keep_their_own_prompt(self):
        barrier, thread = Barrier(2), local()
        def load(uri):
            return types.SimpleNamespace(name='restaurant-assistant-prompt', version=thread.version, template='Hello {date}')
        def graph(state, **kwargs):
            thread.version = state['slug']
            app.load_system_prompt()
            barrier.wait(timeout=5)
            app.load_system_prompt()
            return {'messages': [AIMessage(content='hello')]}
        with patch.object(app, 'MLFLOW_URI', 'https://mlflow.example.com'), patch.object(app.mlflow.genai, 'load_prompt', side_effect=load), patch.object(app.mlflow, 'update_current_trace'), patch.object(app._graph, 'invoke', side_effect=graph):
            with ThreadPoolExecutor(max_workers=2) as workers:
                results = list(workers.map(lambda slug: app._run_assistant_turn([], slug, slug), ('2', '3')))
        self.assertEqual([result[3]['version'] for result in results], ['2', '3'])

    def test_one_prompt_version_per_turn_and_fresh_alias_next_turn(self):
        prompts = [types.SimpleNamespace(name='restaurant-assistant-prompt', version=n, template='Today {date}') for n in (2, 3)]
        def graph(state, **kwargs):
            self.assertEqual(app.load_system_prompt(), app.load_system_prompt())
            return {'messages': [AIMessage(content='hello')]}
        with patch.object(app, 'MLFLOW_URI', 'https://mlflow.example.com'), patch.object(app.mlflow.genai, 'load_prompt', side_effect=prompts) as load, patch.object(app.mlflow, 'update_current_trace') as update, patch.object(app._graph, 'invoke', side_effect=graph):
            first = app._run_assistant_turn([], 'session-one', 'sakura')
            second = app._run_assistant_turn([], 'session-two', 'sakura')
        self.assertEqual(first[3]['version'], '2')
        self.assertEqual(second[3]['version'], '3')
        self.assertEqual(load.call_count, 2)
        self.assertIsNone(app._turn_details.get())
        self.assertTrue(any(call.kwargs.get('session_id') == 'session-one' for call in update.call_args_list))

    def test_formatter_failure_is_visible(self):
        prompt = types.SimpleNamespace(name='test', version=2, template='Missing {unsupported}')
        token = app._turn_details.set({})
        try:
            with patch.object(app, 'MLFLOW_URI', 'https://mlflow.example.com'), patch.object(app.mlflow.genai, 'load_prompt', return_value=prompt), patch.object(app.mlflow, 'update_current_trace'):
                rendered = app.load_system_prompt()
            self.assertIn('reservation', rendered)
            self.assertEqual(app._turn_details.get()['prompt']['status'], 'fallback')
        finally:
            app._turn_details.reset(token)

    def test_blocked_turn_does_not_claim_prompt_version(self):
        with patch.object(app._graph, 'invoke', return_value={'messages': [AIMessage(content='blocked')]}):
            result = app._run_assistant_turn([], 'blocked-session', 'sakura')
        self.assertEqual(result[3], {'status': 'not_used'})

    def test_trace_link_includes_workspace_and_path_prefix(self):
        with patch.object(app, 'MLFLOW_UI_URL', 'https://ai.example.com/mlflow'), patch.object(app, 'EXPERIMENT_ID', '42'), patch.dict(os.environ, {'MLFLOW_WORKSPACE': 'tableschnappi-user1'}):
            self.assertEqual(app.trace_url('tr-123'), 'https://ai.example.com/mlflow/#/experiments/42/traces/tr-123?workspace=tableschnappi-user1')
        with patch.object(app, 'MLFLOW_UI_URL', ''):
            self.assertIsNone(app.trace_url('tr-123'))

    def test_feedback_persist_failure_and_retry(self):
        with TestClient(app.app) as client:
            with patch.object(app.mlflow, 'log_feedback', side_effect=RuntimeError('tracking unavailable')):
                response = client.post('/feedback', json={'traceId': 'tr-test', 'score': 1})
            self.assertEqual(response.status_code, 502)
            self.assertFalse(response.json()['ok'])
            with patch.object(app.mlflow, 'log_feedback') as log:
                response = client.post('/feedback', json={'traceId': 'tr-test', 'score': 0})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(log.call_args.kwargs['value'], False)
            self.assertEqual(client.post('/feedback', json={'traceId': 'tr-test', 'score': 3}).status_code, 400)
            self.assertEqual(client.post('/feedback', json={'traceId': 'tr-test'}).status_code, 400)

    def test_guard_failure_and_disabled_are_distinct(self):
        span = Mock()
        with patch.object(app, 'MLFLOW_URI', 'https://mlflow.example.com'), patch.object(app.mlflow, 'get_current_active_span', return_value=span):
            app._shield_check('hello')
            span.set_attribute.assert_called_with('guardrails.outcome', 'skipped')
            with patch.object(app, 'SHIELD_ENABLED', True), patch.object(app.httpx, 'post', side_effect=RuntimeError('cold')):
                app._shield_check('hello')
            span.set_attribute.assert_called_with('guardrails.outcome', 'error_fail_open')


if __name__ == '__main__':
    unittest.main()
