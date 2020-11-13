import json


async def test_get_spec(jp_fetch):
    response = await jp_fetch("api", "spec.yaml", method="GET")
    assert response.code == 200


async def test_get_status(jp_fetch):
    response = await jp_fetch("api", "status", method="GET")
    assert response.code == 200
    assert response.headers.get("Content-Type") == "application/json"
    status = json.loads(response.body.decode("utf8"))
    assert sorted(status.keys()) == [
        "connections",
        "kernels",
        "last_activity",
        "started",
    ]
    assert status["connections"] == 0
    assert status["kernels"] == 0
    assert status["last_activity"].endswith("Z")
    assert status["started"].endswith("Z")
