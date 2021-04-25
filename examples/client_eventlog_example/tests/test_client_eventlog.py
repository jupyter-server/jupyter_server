import json


EVENT = {
    'schema': 'https://example.jupyter.org/client-event',
    'version': 1.0,
    'event': {
        'user': 'user',
        'thing': 'thing'
    }
}


async def test_client_eventlog(jp_eventlog_sink, jp_fetch):
    serverapp, sink = jp_eventlog_sink
    serverapp.eventlog.allowed_schemas = {
        EVENT['schema']: {
            'allowed_categories': [
                'category.jupyter.org/unrestricted',
                'category.jupyter.org/user-identifier'
            ]
        }
    }

    r = await jp_fetch(
        'api',
        'eventlog',
        method='POST',
        body=json.dumps(EVENT)
    )
    assert r.code == 204

    output = sink.getvalue()
    assert output
    data = json.loads(output)
    assert EVENT['event'].items() <= data.items()
