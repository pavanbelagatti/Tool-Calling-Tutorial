from types import SimpleNamespace
from unittest.mock import Mock, patch

with patch("openai.OpenAI"):
    import main


def test_wikipedia_schema_and_routing(monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value.choices = [Mock(message=Mock(
        function_call=SimpleNamespace(
            name="get_wikipedia_summary",
            arguments='{"topic": "Ada Lovelace"}',
        ),
    ))]
    monkeypatch.setattr(main, "client", client)
    result = {
        "title": "Ada Lovelace",
        "summary": "An English mathematician and writer.",
        "url": "https://en.wikipedia.org/wiki/Ada_Lovelace",
    }
    with patch("main.get_wikipedia_summary", return_value=result) as lookup:
        assert main.ask_llm(
            "Give me a short summary of Ada Lovelace from Wikipedia"
        ) == result
        lookup.assert_called_once_with(topic="Ada Lovelace")

    functions = client.chat.completions.create.call_args.kwargs["functions"]
    schema = next(f for f in functions if f["name"] == "get_wikipedia_summary")
    assert schema["parameters"] == {
        "type": "object",
        "properties": {"topic": {"type": "string"}},
        "required": ["topic"],
    }
