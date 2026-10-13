from unittest.mock import patch

import pytest
import requests

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

    assert get_joke() == {"error": "Joke API error: 503 Service Unavailable"}
    mock_get.return_value.json.assert_not_called()
