from unittest.mock import Mock, patch

import pytest
import requests

import tools

from tools import convert_currency, get_crypto_price, get_joke


@pytest.fixture(autouse=True)
def mock_get():
    with patch("tools.requests.get") as mocked_get:
        yield mocked_get


def test_crypto_price_success(mock_get):
    mock_get.return_value.json.return_value = {"bitcoin": {"usd": 65000}}

    assert get_crypto_price(" btc ") == {
        "symbol": "BTC",
        "price_usd": 65000,
        "source": "CoinGecko",
    }
    mock_get.assert_called_once_with(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        timeout=10,
    )
    mock_get.return_value.raise_for_status.assert_called_once_with()


def test_crypto_price_missing_data(mock_get):
    mock_get.return_value.json.return_value = {}

    assert get_crypto_price("BTC") == {"error": "Price not found for 'BTC'"}


def test_currency_conversion_success(mock_get):
    mock_get.return_value.json.return_value = {"rates": {"EUR": 0.92345}}

    assert convert_currency(10, "usd", "eur") == {
        "amount": 10,
        "from": "USD",
        "to": "EUR",
        "converted_amount": 9.23,
    }
    mock_get.assert_called_once_with(
        "https://open.er-api.com/v6/latest/USD", timeout=10,
    )
    mock_get.return_value.raise_for_status.assert_called_once_with()


def test_currency_conversion_missing_rate(mock_get):
    mock_get.return_value.json.return_value = {"rates": {}}

    assert convert_currency(10, "USD", "EUR") == {
        "error": "Cannot convert USD to EUR",
    }


def test_joke_success(mock_get):
    mock_get.return_value.json.return_value = {
        "setup": "Why did the chicken cross the road?",
        "punchline": "To get to the other side.",
    }

    assert get_joke() == {
        "setup": "Why did the chicken cross the road?",
        "punchline": "To get to the other side.",
    }
    mock_get.assert_called_once_with(
        "https://official-joke-api.appspot.com/random_joke", timeout=10,
    )
    mock_get.return_value.raise_for_status.assert_called_once_with()


def test_joke_http_error(mock_get):
    mock_get.return_value.raise_for_status.side_effect = requests.HTTPError(
        "503 Service Unavailable"
    )

    assert get_joke() == {"error": "Joke API error: Unable to fetch data. Please try again later."}
    mock_get.return_value.json.assert_not_called()


TOOL_CALLS = [
    (tools.get_weather, ("London",)),
    (tools.get_sunrise_sunset, ("Tokyo",)),
    (tools.get_ai_news, ()),
    (tools.get_crypto_price, ("BTC",)),
    (tools.convert_currency, (10, "USD", "EUR")),
    (tools.get_fun_fact, ()),
    (tools.get_joke, ()),
    (tools.get_advice, ()),
    (tools.get_meme, ()),
    (tools.define_word, ("hello",)),
    (tools.chuck_joke, ()),
    (tools.get_ip_info, ()),
    (tools.get_cat_fact, ()),
    (tools.get_dog_image, ()),
    (tools.get_air_quality, ("London",)),
    (tools.get_github_repo, ("owner", "repo")),
    (tools.get_public_holidays, ("DE", 2026)),
]


@pytest.mark.parametrize("tool,args", TOOL_CALLS)
@pytest.mark.parametrize("failure", ["timeout", "connection", "http", "json"])
def test_tools_return_friendly_api_errors(mock_get, tool, args, failure):
    if failure == "timeout":
        mock_get.side_effect = requests.Timeout("private details")
    elif failure == "connection":
        mock_get.side_effect = requests.ConnectionError("private details")
    elif failure == "http":
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError(
            "private details"
        )
    else:
        mock_get.return_value.json.side_effect = ValueError("private details")

    result = tool(*args)

    assert list(result) == ["error"]
    assert result["error"].endswith(
        "Unable to fetch data. Please try again later."
    )
    assert "private details" not in result["error"]
    assert mock_get.call_args.kwargs["timeout"] == 10
    if failure == "http":
        mock_get.return_value.json.assert_not_called()


@pytest.mark.parametrize("tool", [tools.get_weather, tools.get_air_quality, tools.get_sunrise_sunset])
def test_second_api_call_failure(mock_get, tool):
    geocoding = Mock()
    geocoding.json.return_value = {
        "results": [{"latitude": 51.5, "longitude": -0.1}]
    }
    mock_get.side_effect = [geocoding, requests.Timeout("private details")]

    assert tool("London")["error"].endswith(
        "Unable to fetch data. Please try again later."
    )
    assert mock_get.call_count == 2
    assert all(call.kwargs["timeout"] == 10 for call in mock_get.call_args_list)


def test_get_json_forwards_parameters_and_headers(mock_get):
    mock_get.return_value.json.return_value = {"result": "ok"}

    assert tools._get_json(
        "https://example.com", params={"q": "hello"}, headers={"Accept": "application/json"}
    ) == {"result": "ok"}
    mock_get.assert_called_once_with(
        "https://example.com", timeout=10,
        params={"q": "hello"}, headers={"Accept": "application/json"},
    )
    mock_get.return_value.raise_for_status.assert_called_once_with()


def test_public_holidays_success(mock_get):
    mock_get.return_value.json.return_value = [{
        "date": "2026-01-01", "name": "New Year's Day", "localName": "Neujahr",
        "countryCode": "DE", "global": True, "types": ["Public"],
    }]

    assert tools.get_public_holidays(" de ", 2026) == [{
        "date": "2026-01-01", "name": "New Year's Day", "local_name": "Neujahr",
    }]
    mock_get.assert_called_once_with(
        "https://date.nager.at/api/v3/PublicHolidays/2026/DE", timeout=10,
    )


def test_public_holidays_defaults_to_current_year(mock_get):
    mock_get.return_value.json.return_value = []
    with patch("tools.date") as mock_date:
        mock_date.today.return_value.year = 2030
        assert tools.get_public_holidays("US") == []
    mock_get.assert_called_once_with(
        "https://date.nager.at/api/v3/PublicHolidays/2030/US", timeout=10,
    )


@pytest.mark.parametrize("country_code", ["", "India", "12", "../", "éé"])
def test_public_holidays_invalid_country_code(mock_get, country_code):
    assert "error" in tools.get_public_holidays(country_code, 2026)
    mock_get.assert_not_called()


def test_public_holidays_unknown_country_code(mock_get):
    mock_get.return_value.raise_for_status.side_effect = requests.HTTPError("404")
    assert "error" in tools.get_public_holidays("ZZ", 2026)
    mock_get.return_value.json.assert_not_called()


def test_sunrise_sunset_success(mock_get):
    results = {
        "sunrise": "2026-10-21T20:53:00+00:00",
        "sunset": "2026-10-22T07:58:00+00:00",
        "day_length": 39900,
    }
    mock_get.return_value.json.side_effect = [
        {"results": [{"latitude": 35.68, "longitude": 139.69}]},
        {"status": "OK", "results": {**results, "solar_noon": "unused"}},
    ]

    assert tools.get_sunrise_sunset("Tokyo") == {"city": "Tokyo", **results}
    assert mock_get.call_count == 2
    assert mock_get.call_args_list[0].args == (
        "https://geocoding-api.open-meteo.com/v1/search",
    )
    assert mock_get.call_args_list[0].kwargs == {
        "params": {"name": "Tokyo", "count": 1, "language": "en", "format": "json"},
        "timeout": 10,
    }
    mock_get.assert_called_with(
        "https://api.sunrise-sunset.org/json",
        params={"lat": 35.68, "lng": 139.69, "formatted": 0}, timeout=10,
    )


def test_sunrise_sunset_unknown_city(mock_get):
    mock_get.return_value.json.return_value = {"results": []}

    assert tools.get_sunrise_sunset("Unknown City") == {
        "error": "City 'Unknown City' not found",
    }
    assert mock_get.call_count == 1


def test_sunrise_sunset_api_error_status(mock_get):
    mock_get.return_value.json.side_effect = [
        {"results": [{"latitude": 35.68, "longitude": 139.69}]},
        {"status": "UNKNOWN_ERROR", "results": ""},
    ]

    assert tools.get_sunrise_sunset("Tokyo") == {
        "error": "Sunrise-sunset API error: Unable to fetch data. Please try again later.",
    }
