import os
import json
from openai import OpenAI

from tools import (
    get_weather,
    get_sunrise_sunset,
    get_air_quality,
    get_ai_news,
    get_crypto_price,
    convert_currency,
    get_fun_fact,
    get_joke,
    get_advice,
    get_meme,
    define_word,
    chuck_joke,
    get_ip_info,
    get_cat_fact,
    get_dog_image,
    get_github_repo,
    get_public_holidays,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FUNCTIONS = [
    {
        "name": "get_public_holidays",
        "description": "List public holiday dates and names for a country.",
        "parameters": {
            "type": "object",
            "properties": {
                "country_code": {
                    "type": "string",
                    "description": "ISO 3166-1 alpha-2 country code, such as IN, DE, or US.",
                },
                "year": {"type": "integer", "description": "Year to query; defaults to the current year."},
            },
            "required": ["country_code"],
        },
    },
    {
        "name": "get_weather",
        "description": "Get weather + umbrella/jacket advice.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "get_sunrise_sunset",
        "description": "Get today's sunrise and sunset times in UTC and day length in seconds for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "get_air_quality",
        "description": "Get air quality for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "get_ai_news",
        "description": "Fetch AI news (top 5).",
        "parameters": {
            "type": "object",
            "properties": {"region": {"type": "string"}},
        },
    },
    {
        "name": "get_crypto_price",
        "description": "Get crypto price.",
        "parameters": {
            "type": "object",
            "properties": {"symbol": {"type": "string"}},
            "required": ["symbol"],
        },
    },
    {
        "name": "convert_currency",
        "description": "Convert between currencies.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string"},
                "to_currency": {"type": "string"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
    {"name": "get_fun_fact", "description": "Fun fact", "parameters": {"type": "object", "properties": {}}},
    {"name": "get_joke", "description": "Random joke", "parameters": {"type": "object", "properties": {}}},
    {"name": "get_advice", "description": "Life advice", "parameters": {"type": "object", "properties": {}}},
    {"name": "get_meme", "description": "Fetch meme", "parameters": {"type": "object", "properties": {}}},
    {
        "name": "define_word",
        "description": "Dictionary meaning.",
        "parameters": {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]},
    },
    {"name": "chuck_joke", "description": "Chuck Norris joke", "parameters": {"type": "object", "properties": {}}},
    {"name": "get_ip_info", "description": "IP geolocation", "parameters": {"type": "object", "properties": {}}},
    {"name": "get_cat_fact", "description": "Cat fact", "parameters": {"type": "object", "properties": {}}},
    {"name": "get_dog_image", "description": "Dog image", "parameters": {"type": "object", "properties": {}}},
    {
        "name": "get_github_repo",
        "description": "Get public GitHub repository details, including stars, forks, and language.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
            },
            "required": ["owner", "repo"],
        },
    },
]


def ask_llm(user_input: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}],
        functions=FUNCTIONS,
        function_call="auto",
    )

    msg = response.choices[0].message

    if msg.function_call:
        fn = msg.function_call.name
        args = json.loads(msg.function_call.arguments or "{}")

        if fn == "get_weather": return get_weather(**args)
        if fn == "get_sunrise_sunset": return get_sunrise_sunset(**args)
        if fn == "get_air_quality": return get_air_quality(**args)
        if fn == "get_ai_news": return get_ai_news(**args)
        if fn == "get_crypto_price": return get_crypto_price(**args)
        if fn == "convert_currency": return convert_currency(**args)
        if fn == "get_fun_fact": return get_fun_fact()
        if fn == "get_joke": return get_joke()
        if fn == "get_advice": return get_advice()
        if fn == "get_meme": return get_meme()
        if fn == "define_word": return define_word(**args)
        if fn == "chuck_joke": return chuck_joke()
        if fn == "get_ip_info": return get_ip_info()
        if fn == "get_cat_fact": return get_cat_fact()
        if fn == "get_dog_image": return get_dog_image()
        if fn == "get_github_repo": return get_github_repo(**args)
        if fn == "get_public_holidays": return get_public_holidays(**args)

        return {"error": f"Unknown tool '{fn}'"}

    return msg.content


if __name__ == "__main__":
    while True:
        try:
            q = input("You: ")
            if q.strip():
                print("AI:", ask_llm(q))
        except (EOFError, KeyboardInterrupt):
            break
