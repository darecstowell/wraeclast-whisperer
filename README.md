# Wraeclast Whisperer

An AI-powered assistant for Path of Exile 2 that helps players optimize their gaming experience.

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
2. Copy `.env.example` to `.env` and add your OpenAI API key
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
Install Extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
Use command -- "Dev Containers: Rebuild Container" 

## Configuration

Set your OpenAI API key in the .env file:

```env
OPENAI_API_KEY=your-api-key-here
```

## Development

This project uses:

- Poetry for dependency management
- Black for code formatting
- Ruff for linting
- MyPy for type checking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Path of Exile 2 and all related content are property of Grinding Gear Games. Go Support them!
