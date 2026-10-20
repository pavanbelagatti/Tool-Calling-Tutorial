## 🚀 Tool Calling AI Assistant — Python + OpenAI + Streamlit

A complete, beginner-friendly, real-world tutorial on building Tool-Calling AI Assistants that fetch live data using multiple APIs.
This project demonstrates how to connect an LLM to real-world tools like weather, air quality, AI news, crypto prices, currency conversion, memes, jokes, advice, dictionary meanings, and more — all inside a clean Streamlit UI.

## ✨ Features
🔥 Real-World Tool Calls
Your AI assistant can:
- 🌦 Live weather with umbrella + jacket recommendations
- 🌅 Today's sunrise and sunset in UTC + day length in seconds ([Sunrise-Sunset.org](https://sunrise-sunset.org/))
- 🏭 Air quality (PM2.5, PM10, US AQI + category)
- 📰 Top AI news (cleaned + fallback links)
- 🪙 Crypto prices (BTC, ETH, SOL, DOGE…)
- 💱 Currency conversion
- 📅 Public holiday dates and names by country and year (Nager.Date coverage)
- 😂 Jokes, fun facts, advice
- 📸 Memes + dog images
- 📖 Word definitions
- 🌍 IP geolocation
- 💻 Public GitHub repository details (description, stars, forks, language)

Try asking: "Show me the GitHub repository pavanbelagatti/Tool-Calling-Tutorial."
This action uses the [GitHub REST API](https://docs.github.com/en/rest/repos/repos#get-a-repository) without an additional API key; unauthenticated rate limits apply.

### 🎨 Beautiful Streamlit Chat UI
- Chat-style interface
- Displays images
- Clean JSON backend
- Real-time responses
- Easy to extend

### 🧠 Fully Automated Tool Routing
The LLM decides which tool to call and passes arguments automatically using OpenAI Tool Calling.

### Project Structure
```
tool-calling/
│
├── tools.py        # All real API functions (weather, AQI, crypto, news, etc.)
├── main.py         # LLM logic + tool schemas + routing
├── ui.py           # Streamlit UI for chatting with the assistant
├── requirements.txt
└── README.md
```

### ⚙️ Setup & Installation
#### Clone the repo

```
git clone https://github.com/pavanbelagatti/Tool-Calling-Tutorial.git
```

```
cd Tool-Calling-Tutorial
```

#### Create a virtual environment

```
python3 -m venv venv
```

```
source venv/bin/activate
```

#### Install dependencies
```
pip install -r requirements.txt
```

#### Set your OpenAI API key
```
export OPENAI_API_KEY="your_api_key_here"
```

#### Run the App
```
streamlit run ui.py
```

### Running tests

From the repository root, run:

```bash
pytest
```

Tests mock HTTP requests and require no network access or API keys.
