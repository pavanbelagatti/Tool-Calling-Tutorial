import importlib
from types import SimpleNamespace
from unittest.mock import patch


def test_sunrise_sunset_schema_and_routing():
    with patch("openai.OpenAI"):
        main = importlib.import_module("main")

    schema = next(tool for tool in main.FUNCTIONS if tool["name"] == "get_sunrise_sunset")
    assert schema["parameters"] == {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    }
    message = SimpleNamespace(function_call=SimpleNamespace(
        name="get_sunrise_sunset", arguments='{"city": "Tokyo"}',
    ))
    with patch.object(main, "client") as client, patch.object(main, "get_sunrise_sunset") as tool:
        client.chat.completions.create.return_value.choices = [SimpleNamespace(message=message)]
        tool.return_value = {"city": "Tokyo", "sunrise": "sunrise", "sunset": "sunset", "day_length": 39900}

        assert main.ask_llm("When does the sun set in Tokyo today?") == tool.return_value
        tool.assert_called_once_with(city="Tokyo")
