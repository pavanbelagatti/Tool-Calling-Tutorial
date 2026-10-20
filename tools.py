from datetime import date
from urllib.parse import quote

import requests


class APIError(Exception):
    """A public API request failed with a user-friendly message."""


def _get_json(url, params=None, headers=None):
    """Fetch JSON with a bounded wait and consistent request errors."""
    kwargs = {"timeout": 10}
    if params is not None:
        kwargs["params"] = params
    if headers is not None:
        kwargs["headers"] = headers
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        raise APIError("Unable to fetch data. Please try again later.") from e


# ============================================================
# 1) WEATHER (Open-Meteo, with umbrella + jacket advice)
# ============================================================

def get_weather(city: str):
    """Get live weather with precipitation probability, umbrella advice, and jacket advice."""
    try:
        # 1) City → coordinates
        geo = _get_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )

        if not geo.get("results"):
            return {"error": f"City '{city}' not found"}

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        # 2) Weather
        data = _get_json(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "precipitation_probability",
            },
        )

        current = data.get("current_weather", {})
        hourly_probs = data.get("hourly", {}).get("precipitation_probability", [])
        precip_prob = hourly_probs[0] if hourly_probs else None

        # Umbrella rule
        def umbrella_advice(prob):
            if prob is None:
                return "Rain probability unavailable — cannot determine umbrella need."
            if prob >= 60:
                return "Yes, you should definitely take an umbrella."
            if prob >= 30:
                return "Rain is possible — taking a small umbrella is smart."
            return "No, rain is unlikely — you don’t need an umbrella."

        # Jacket rule
        def jacket_advice(temp):
            if temp is None:
                return "Temperature unavailable — cannot determine jacket needs."
            if temp <= 0:
                return "Yes, it's freezing — wear a heavy winter jacket."
            if temp <= 10:
                return "Yes, it's cold — carry a warm jacket or layers."
            if temp <= 18:
                return "A light jacket is recommended."
            return "No jacket needed — weather is warm."

        temp = current.get("temperature")

        return {
            "city": city,
            "temperature_c": temp,
            "windspeed_kmh": current.get("windspeed"),
            "time": current.get("time"),
            "precipitation_probability_percent": precip_prob,
            "umbrella_recommendation": umbrella_advice(precip_prob),
            "jacket_recommendation": jacket_advice(temp),
        }

    except Exception as e:
        return {"error": f"Weather API error: {e}"}


# ============================================================
# 2) AI NEWS (improved — no NULLs)
# ============================================================

def get_ai_news(region: str = None):
    """Fetch latest AI-related news from HackerNews. Removes null entries."""
    try:
        query = "AI"
        if region:
            query = f"AI {region}"

        resp = _get_json(
            "https://hn.algolia.com/api/v1/search",
            params={"query": query},
        )
        hits = resp.get("hits", [])

        cleaned = []
        for item in hits:
            title = item.get("title")
            url = item.get("url")
            object_id = item.get("objectID")

            # Skip entries without a title
            if not title:
                continue

            # If no external URL → fallback to HN discussion
            if not url and object_id:
                url = f"https://news.ycombinator.com/item?id={object_id}"

            cleaned.append({"title": title, "url": url})

            if len(cleaned) == 5:
                break

        if not cleaned:
            return {"error": "No AI news found"}

        return cleaned

    except Exception as e:
        return {"error": f"AI news API error: {e}"}


# ============================================================
# 3) CRYPTO PRICE (CoinGecko with symbol mapping)
# ============================================================

def get_crypto_price(symbol: str):
    """
    Get crypto price using CoinGecko.
    Accepts common tickers like BTC, ETH, SOL and maps them to CoinGecko IDs.
    """
    try:
        symbol = symbol.upper().strip()

        COINGECKO_IDS = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "DOGE": "dogecoin",
            "MATIC": "matic-network",
            "BNB": "binancecoin",
            "ADA": "cardano",
            "XRP": "ripple",
        }

        if symbol not in COINGECKO_IDS:
            return {"error": f"Crypto '{symbol}' not recognized. Try BTC, ETH, SOL, DOGE, etc."}

        coingecko_id = COINGECKO_IDS[symbol]

        data = _get_json(
            f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd",
        )

        if coingecko_id not in data:
            return {"error": f"Price not found for '{symbol}'"}

        return {
            "symbol": symbol,
            "price_usd": data[coingecko_id]["usd"],
            "source": "CoinGecko",
        }

    except Exception as e:
        return {"error": f"Crypto API error: {e}"}


# ============================================================
# 4) CURRENCY CONVERSION
# ============================================================

def convert_currency(amount: float, from_currency: str, to_currency: str):
    try:
        data = _get_json(
            f"https://open.er-api.com/v6/latest/{from_currency.upper()}",
        )
        rates = data.get("rates", {})

        if to_currency.upper() not in rates:
            return {"error": f"Cannot convert {from_currency} to {to_currency}"}

        converted = amount * rates[to_currency.upper()]

        return {
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "converted_amount": round(converted, 2),
        }
    except Exception as e:
        return {"error": f"Currency conversion API error: {e}"}


# ============================================================
# 5) FUN FACT
# ============================================================

def get_fun_fact():
    try:
        r = _get_json("https://uselessfacts.jsph.pl/random.json?language=en")
        return {"fact": r.get("text")}
    except Exception as e:
        return {"error": f"Fun fact API error: {e}"}


# ============================================================
# 6) RANDOM JOKE
# ============================================================

def get_joke():
    try:
        joke = _get_json("https://official-joke-api.appspot.com/random_joke")
        return {"setup": joke.get("setup"), "punchline": joke.get("punchline")}
    except Exception as e:
        return {"error": f"Joke API error: {e}"}


# ============================================================
# 7) RANDOM ADVICE
# ============================================================

def get_advice():
    try:
        r = _get_json("https://api.adviceslip.com/advice")
        return {"advice": r["slip"]["advice"]}
    except Exception as e:
        return {"error": f"Advice API error: {e}"}


# ============================================================
# 8) RANDOM MEME
# ============================================================

def get_meme():
    try:
        j = _get_json("https://meme-api.com/gimme")
        return {
            "title": j.get("title"),
            "image_url": j.get("url"),
            "subreddit": j.get("subreddit"),
        }
    except Exception as e:
        return {"error": f"Meme API error: {e}"}


# ============================================================
# 9) DICTIONARY
# ============================================================

def define_word(word: str):
    try:
        data = _get_json(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")

        meanings = []
        for m in data[0].get("meanings", []):
            meanings.append({
                "part_of_speech": m.get("partOfSpeech"),
                "definitions": [d.get("definition") for d in m.get("definitions", [])],
            })

        return {"word": word, "meanings": meanings}
    except Exception as e:
        return {"error": f"Dictionary API error: {e}"}


# ============================================================
# 10) CHUCK NORRIS JOKE
# ============================================================

def chuck_joke():
    try:
        r = _get_json("https://api.chucknorris.io/jokes/random")
        return {"joke": r.get("value")}
    except Exception as e:
        return {"error": f"Chuck Norris API error: {e}"}


# ============================================================
# 11) IP GEOLOCATION
# ============================================================

def get_ip_info():
    try:
        r = _get_json("https://ipapi.co/json/")
        return r
    except Exception as e:
        return {"error": f"IP API error: {e}"}


# ============================================================
# 12) CAT FACT
# ============================================================

def get_cat_fact():
    try:
        r = _get_json("https://catfact.ninja/fact")
        return {"fact": r.get("fact")}
    except Exception as e:
        return {"error": f"Cat fact API error: {e}"}


# ============================================================
# 13) DOG IMAGE
# ============================================================

def get_dog_image():
    try:
        r = _get_json("https://dog.ceo/api/breeds/image/random")
        return {"image_url": r.get("message")}
    except Exception as e:
        return {"error": f"Dog API error: {e}"}


# ============================================================
# 14) AIR QUALITY (Open-Meteo Air Quality API)
# ============================================================

def get_air_quality(city: str):
    """
    Get air quality info (PM2.5, PM10, US AQI) for any city on earth.
    Uses Open-Meteo geocoding + air-quality API (no API key).
    """
    try:
        # 1) City → coordinates
        geo = _get_json(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )

        if not geo.get("results"):
            return {"error": f"City '{city}' not found"}

        loc = geo["results"][0]
        lat = loc["latitude"]
        lon = loc["longitude"]

        # 2) Air Quality
        aq = _get_json(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={"latitude": lat, "longitude": lon, "hourly": "pm2_5,pm10,us_aqi"},
        )

        times = aq.get("hourly", {}).get("time", [])
        pm25_list = aq.get("hourly", {}).get("pm2_5", [])
        pm10_list = aq.get("hourly", {}).get("pm10", [])
        aqi_list = aq.get("hourly", {}).get("us_aqi", [])

        if not times:
            return {"error": f"No air quality data for '{city}'"}

        pm25 = pm25_list[0] if pm25_list else None
        pm10 = pm10_list[0] if pm10_list else None
        aqi = aqi_list[0] if aqi_list else None

        # AQI classification
        def aqi_cat(v):
            if v is None:
                return "Unknown"
            v = float(v)
            if v <= 50:
                return "Good"
            if v <= 100:
                return "Moderate"
            if v <= 150:
                return "Unhealthy for Sensitive Groups"
            if v <= 200:
                return "Unhealthy"
            if v <= 300:
                return "Very Unhealthy"
            return "Hazardous"

        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "time": times[0],
            "pm2_5": pm25,
            "pm10": pm10,
            "us_aqi": aqi,
            "us_aqi_category": aqi_cat(aqi),
            "source": "Open-Meteo Air Quality",
        }

    except Exception as e:
        return {"error": f"Air quality API error: {e}"}


# ============================================================
# 15) GITHUB REPOSITORY
# ============================================================

def get_github_repo(owner: str, repo: str):
    """Get public GitHub repository details without an API key."""
    try:
        owner = owner.strip()
        repo = repo.strip()
        if not owner or not repo:
            return {"error": "GitHub owner and repository name are required"}

        data = _get_json(
            f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(repo, safe='')}",
            headers={"Accept": "application/vnd.github+json"},
        )
        return {
            "repository": data.get("full_name"),
            "description": data.get("description"),
            "url": data.get("html_url"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "language": data.get("language"),
        }
    except Exception as e:
        return {"error": f"GitHub API error: {e}"}


# ============================================================
# 16) PUBLIC HOLIDAYS (Nager.Date)
# ============================================================

def get_public_holidays(country_code: str, year: int | None = None):
    """Get public holiday dates and names for a country without an API key."""
    try:
        country_code = country_code.strip().upper()
        if len(country_code) != 2 or not country_code.isascii() or not country_code.isalpha():
            return {"error": "Use a two-letter ISO country code, such as IN, DE, or US."}

        if year is None:
            year = date.today().year

        data = _get_json(
            f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}",
        )
        return [
            {"date": holiday["date"], "name": holiday["name"], "local_name": holiday["localName"]}
            for holiday in data
        ]
    except Exception as e:
        return {"error": f"Public holidays API error: {e}"}
