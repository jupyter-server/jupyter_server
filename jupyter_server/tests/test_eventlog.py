import json

import jsonschema
import pytest

from jupyter_server.utils import eventlogging_schema_fqn
from .services.contents.test_api import contents, contents_dir, dirs


@pytest.mark.parametrize('path, name', dirs)
async def test_eventlog_list_notebooks(jp_eventlog_sink, jp_fetch, contents, path, name):
    schema, version = (eventlogging_schema_fqn('contentsmanager-actions'), 1)
    serverapp, sink = jp_eventlog_sink
    serverapp.eventlog.allowed_schemas = {
        serverapp.eventlog.schemas[(schema, version)]['$id']: {
            'allowed_categories': [
                'category.jupyter.org/unrestricted',
                'category.jupyter.org/user-identifiable-information'
            ]
        }
    }

    r = await jp_fetch(
        'api',
        'contents',
        path,
        method='GET',
    )
    assert r.code == 200

    output = sink.getvalue()
    assert output
    data = json.loads(output)
    jsonschema.validate(data, serverapp.eventlog.schemas[(schema, version)])
    expected = {'action': 'get', 'path': path}
    assert expected.items() <= data.items()
