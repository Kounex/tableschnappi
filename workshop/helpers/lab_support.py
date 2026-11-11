"""Small end-to-end comparison: call the restaurant, retain its real trace IDs."""
import json
import os
from pathlib import Path
import time
import uuid

import mlflow
import pandas as pd
from mlflow import MlflowClient
import requests

PROMPT_NAME = 'restaurant-assistant-prompt'


def active_prompt():
    return mlflow.genai.load_prompt(f'prompts:/{PROMPT_NAME}@active', cache_ttl_seconds=0)


def run_cases(variant):
    """Run after selecting @active in MLflow; never publish or move an alias here."""
    if variant not in ('baseline', 'candidate'):
        raise ValueError('Choose baseline or candidate')
    base = os.environ['RESTAURANT_API_URL'].rstrip('/')
    selected = str(active_prompt().version)
    cases = json.loads((Path(__file__).with_name('restaurant-cases.json')).read_text())
    rows = []
    mlflow.set_experiment('restaurant-workshop-comparison')
    with mlflow.start_run(run_name=f'{variant}-prompt-v{selected}'):
        mlflow.log_params({'variant': variant, 'prompt_version': selected, 'cases': len(cases)})
        for case in cases:
            if str(active_prompt().version) != selected:
                raise RuntimeError('Active prompt changed during comparison; rerun this batch')
            started = time.monotonic()
            response = requests.post(f'{base}/api/restaurants/sakura/assistant', json={
                'sessionId': str(uuid.uuid4()),
                'messages': [{'role': 'user', 'content': case['question']}],
            }, timeout=120)
            elapsed = round(time.monotonic() - started, 2)
            response.raise_for_status()
            result = response.json()
            info = result.get('prompt', {})
            if info.get('status') == 'fallback' or (info.get('status') == 'registry' and str(info.get('version')) != selected):
                raise RuntimeError('App used a fallback or different prompt; inspect configuration before comparing')
            trace_id = result.get('traceId')
            if not trace_id:
                raise RuntimeError('App returned no trace ID; check MLflow integration')
            # Trace export can finish after the HTTP response. Verify actual storage.
            for attempt in range(10):
                trace = mlflow.get_trace(trace_id)
                if trace is not None:
                    break
                time.sleep(1)
            else:
                raise RuntimeError(f'App trace was not readable: {trace_id}')
            for key, value in {'lab.case': case['id'], 'lab.variant': variant}.items():
                MlflowClient().set_trace_tag(trace_id, key, value)
            answer = result.get('response', '')
            tools = [tool['name'] for tool in result.get('toolCalls', [])]
            expected = case.get('expected_tool')
            rows.append({
                'case': case['id'], 'question': case['question'], 'variant': variant,
                'selected_prompt_version': selected, 'used_prompt_version': info.get('version'),
                'prompt_status': info.get('status'), 'answer': answer, 'tools': tools,
                'tool_expectation_met': expected in tools if expected else not tools,
                'has_sections': all(title in answer for title in ('Answer', 'Evidence', 'Next step')),
                'seconds': elapsed,
                'trace_id': trace_id, 'trace_url': result.get('traceUrl'),
            })
        mlflow.log_table(pd.DataFrame(rows), artifact_file='comparison.json')
        mlflow.log_metrics({
            'mean_seconds': sum(row['seconds'] for row in rows) / len(rows),
            'tool_expectation_rate': sum(row['tool_expectation_met'] for row in rows) / len(rows),
            'section_rate': sum(row['has_sections'] for row in rows) / len(rows),
        })
    return rows
