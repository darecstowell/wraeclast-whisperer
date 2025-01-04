# Wraeclast Whisperer

A GPT-powered agent for Path of Exile 2 with up-to-date game data that helps players synergize their builds, create loot filters, answer game-related questions, and more.

![alt text](screenshots/lvl3_support_gems.png)

## Description

Wraeclast Whisperer is an intelligent agent powered by OpenAI's Assistant API that provides personalized guidance for Path of Exile 2 players. It analyzes current game data and player statistics to offer insights and recommendations. This agent is not intended to create builds for you, but rather aid you on your journey. 

## Features (Planned)

- [x] General game knowledge assistance
- [x] Build optimization suggestions
- [ ] Gear improvement recommendations  
- [ ] Skill gem synergy analysis
- [ ] Custom loot filter generation
- [ ] Real-time build assessment

## Prerequisites

- [OpenAI API key](https://platform.openai.com/settings/organization/api-keys)
- [Docker](https://www.docker.com/products/docker-desktop/)

## Installation

1. Clone the repository
2. Copy `app/.env.example` to `app/.env` and add your OpenAI API key
3. Choose your preferred installation method:

**Using Docker**
- Install and run [Docker](https://www.docker.com/products/docker-desktop/), then -
```sh
docker compose up -d;
```
- Navigate to http://localhost:8080/ in your browser

## Development Instructions

**[Using Devcontainer in VSCode](https://code.visualstudio.com/docs/devcontainers/tutorial) (slightly advanced, but fastest method)** 
- Must have [Docker](https://www.docker.com/products/docker-desktop/) installed. 
- Install Extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
- Use vscode command -- "Dev Containers: Rebuild Container" 

## Development Notes

This project uses:

- Chainlit as an LLM framework with UI
- Poetry for dependency management
- Black for code formatting
- Ruff for linting
- MyPy for type checking
- Fly.io for deployment

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Path of Exile 2 and all related content are property of Grinding Gear Games. Go Support them!
- Chainlit
