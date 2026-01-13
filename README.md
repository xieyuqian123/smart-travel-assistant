# Smart Travel Assistant 🌍✈️

An intelligent travel assistant powered by [LangGraph](https://github.com/langchain-ai/langgraph).

## Features

- 🗺️ **Itinerary Planning** - Create personalized travel itineraries
- 🏨 **Accommodation Recommendations** - Find the best places to stay
- 🍽️ **Local Dining Suggestions** - Discover local cuisine
- 🎯 **Activity Planning** - Plan activities based on preferences

## Project Structure

```
smart-travel-assistant/
├── src/
│   └── travel_assistant/
│       ├── __init__.py
│       ├── state.py      # State definitions
│       ├── graph.py      # Main graph definition
│       ├── nodes.py      # Node functions
│       └── tools.py      # Tool definitions
├── tests/
│   └── test_graph.py
├── pyproject.toml
├── langgraph.json
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-travel-assistant.git
cd smart-travel-assistant
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Web Interface (Recommended)

To launch the interactive web interface:

```bash
uv run streamlit run src/travel_assistant/app.py
```

### Programmatic Usage

```python
from travel_assistant.graph import graph

# Run the travel assistant
result = graph.invoke({
    "messages": [{"role": "user", "content": "Plan a 3-day trip to Tokyo"}]
})
```

## Development

Run tests:
```bash
pytest
```

Lint code:
```bash
ruff check .
```

## License

MIT
