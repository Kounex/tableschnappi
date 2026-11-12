"""Minimal client for this repository's stateless, read-only MCP endpoint.

Agent and tracing code stays visible in agent-playground.ipynb. This module only
handles JSON-RPC/SSE framing and the read-only tool allowlist.
"""
import json
import uuid

import requests

READ_TOOLS = {'get_menu', 'get_wait_time', 'check_table_availability', 'list_restaurants'}


def rpc(url, method, params=None):
    request_id = str(uuid.uuid4())
    response = requests.post(
        url,
        json={'jsonrpc': '2.0', 'id': request_id, 'method': method, 'params': params or {}},
        headers={'Accept': 'application/json, text/event-stream',
                 'X-TableSchnappi-Role': 'readonly'},
        timeout=20,
    )
    response.raise_for_status()
    if 'text/event-stream' in response.headers.get('Content-Type', ''):
        # SSE is UTF-8. requests.text can default to Latin-1 for text/*;
        # Unicode menu bytes then become line separators and corrupt JSON.
        text = response.content.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
        messages = []
        for event in text.split('\n\n'):
            # Only protocol LF separates fields; str.splitlines() would also
            # split valid Unicode line separators inside a JSON string.
            data = [line[5:].removeprefix(' ') for line in event.split('\n')
                    if line.startswith('data:')]
            if data:
                messages.append(json.loads('\n'.join(data)))
        payload = next((message for message in messages if message.get('id') == request_id), None)
    else:
        payload = response.json()
    if not isinstance(payload, dict) or payload.get('id') != request_id:
        raise RuntimeError('MCP did not return a matching JSON-RPC response')
    if payload.get('error'):
        raise RuntimeError(f"MCP error: {payload['error'].get('message', 'Unknown error')}")
    return payload['result']


def list_read_tools(url):
    return [{'type': 'function', 'function': {
        'name': tool['name'], 'description': tool.get('description', ''),
        'parameters': tool['inputSchema'],
    }} for tool in rpc(url, 'tools/list')['tools'] if tool['name'] in READ_TOOLS]


def call_read_tool(url, name, arguments):
    if name not in READ_TOOLS:
        raise ValueError(f'Not a playground read tool: {name}')
    result = rpc(url, 'tools/call', {'name': name, 'arguments': arguments})
    if result.get('isError'):
        raise RuntimeError(f"MCP tool failed: {result.get('content')}")
    return '\n'.join(item['text'] for item in result.get('content', []) if item.get('type') == 'text')
