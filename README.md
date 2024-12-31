# Wraeclast Whisperer

A GPT-powered agent for Path of Exile 2 with up-to-date game data that helps players synergize their builds, create loot filters, answer game-related questions, and more.

## Description

Wraeclast Whisperer is an intelligent agent powered by OpenAI's Assistant API that provides personalized guidance for Path of Exile 2 players. It analyzes current game data and player statistics to offer insights and recommendations. This agent is not intended to create builds for you, but rather aid you on your journey. 

## Features (Planned)

- General game knowledge assistance
- Build optimization suggestions
- Gear improvement recommendations  
- Skill gem synergy analysis
- Custom loot filter generation
- Real-time build assessment

## Prerequisites

- Python 3.12+
- OpenAI API key
- Docker (optional, but highly encouraged)

## Installation

1. Clone the repository
2. Copy `app/.env.example` to `app/.env` and add your OpenAI API key
3. Choose your preferred installation method:

**Using Poetry:**
```sh
poetry install
```

**Using Docker** 
```sh
docker compose up -d
```

**Using Devcontainer in VSCode (fastest method)** 

- Install Extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
- Use command -- "Dev Containers: Rebuild Container" 

## Usage
Open app directory
```sh
cd app;
```

Create an OpenAI assistant
```sh
python create_assistant.py;
```

Run the Chainlit app
```sh
chainlit run app.py --no-cache -w;
```
## Screenshots

![alt text](screenshots/lvl3_support_gems.png)

## Development

This project uses:

- Chainlit as an LLM framework with UI
- Poetry for dependency management
- Black for code formatting
- Ruff for linting
- MyPy for type checking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Path of Exile 2 and all related content are property of Grinding Gear Games. Go Support them!
- Chainlit
