"""A mock extension that defines a duplicate tool name to test conflict handling."""

def jupyter_server_extension_tools():
    return {
        "mock_tool": {  # <-- duplicate on purpose
            "metadata": {
                "name": "mock_tool",
                "description": "Conflicting tool name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            },
            "callable": lambda input: f"Echo again: {input}"
        }
    }

def _load_jupyter_server_extension(serverapp):
    serverapp.log.info("Loaded dupe tool extension.")
