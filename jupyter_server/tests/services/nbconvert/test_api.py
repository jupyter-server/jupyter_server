import json


async def test_list_formats(jp_fetch):
    r = await jp_fetch("api", "nbconvert", method="GET")
    formats = json.loads(r.body.decode())
    # Verify the type of the response.
    assert isinstance(formats, dict)
    # Verify that all returned formats have an
    # output mimetype defined.
    required_keys_present = []
    for name, data in formats.items():
        required_keys_present.append("output_mimetype" in data)
    assert all(required_keys_present), "All returned formats must have a `output_mimetype` key."
