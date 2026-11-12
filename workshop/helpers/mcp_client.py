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
        events = response.text.replace('\r\n', '\n').split('\n\n')
        messages = [json.loads('\n'.join(line[5:].lstrip() for line in event.splitlines()
                                        if line.startswith('data:')))
                    for event in events if any(line.startswith('data:') for line in event.splitlines())]
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
