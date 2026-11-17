"""A mock extension exposing a structured tool."""

def jupyter_server_extension_tools():
    return {
        "mock_tool": {
            "metadata": {
                "name": "mock_tool",
                "description": "A mock tool for testing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            },
            "callable": lambda input: f"Echo: {input}"
        }
    }

def _load_jupyter_server_extension(serverapp):
    serverapp.log.info("Loaded mock tool extension.")
