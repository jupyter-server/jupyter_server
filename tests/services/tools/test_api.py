import json
import pytest

@pytest.fixture
def jp_server_config():
    return {
        "ServerApp": {
            "jpserver_extensions": {
                "tests.extension.mockextensions.mockext_tool": True,
                "tests.extension.mockextensions.mockext_customschema": True,
            }
        }
    }

@pytest.mark.asyncio
async def test_multiple_tools_present(jp_fetch):
    response = await jp_fetch("api", "tools", method="GET")
    assert response.code == 200

    body = json.loads(response.body.decode())
    tools = body["discovered_tools"]

    # Check default schema tool
    assert "mock_tool" in tools
    assert "inputSchema" in tools["mock_tool"]

    # Check custom schema tool
    assert "openai_style_tool" in tools
    assert "parameters" in tools["openai_style_tool"]
