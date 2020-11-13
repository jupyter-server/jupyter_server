import json


async def test_list_formats(jp_fetch):
    r = await jp_fetch(
        'api', 'nbconvert',
        method='GET'
    )
    formats = json.loads(r.body.decode())
    assert isinstance(formats, dict)
    assert 'python' in formats
    assert 'html' in formats
    assert formats['python']['output_mimetype'] == 'text/x-python'
