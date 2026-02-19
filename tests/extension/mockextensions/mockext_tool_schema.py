"""A mock extension that provides a custom validation schema."""

OPENAI_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "parameters": {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            },
            "required": ["input"]
        }
    },
    "required": ["name", "parameters"]
}

def jupyter_server_extension_tools():
    tools = {
        "openai_style_tool": {
            "metadata": {
                "name": "openai_style_tool",
                "description": "Tool using OpenAI-style parameters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            },
            "callable": lambda input: f"Got {input}"
        }
    }
    return (tools, OPENAI_TOOL_SCHEMA)

def _load_jupyter_server_extension(serverapp):
    serverapp.log.info("Loaded mock custom-schema extension.")
