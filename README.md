<div align="center">

# Wraeclast Whisperer

![Python Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdarecstowell%2Fwraeclast-whisperer%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.tool.poetry.dependencies.python&label=Python)
![Chainlit Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdarecstowell%2Fwraeclast-whisperer%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.tool.poetry.dependencies.chainlit&label=Chainlit&color=red)
![Last Deployment](https://img.shields.io/github/actions/workflow/status/darecstowell/wraeclast-whisperer/fly-deploy.yml?branch=main&label=Last%20Deployment)

## [✨ Give it a try! ✨](https://wraeclast-whisperer-wispy-brook-8021.fly.dev/)

</div>

A GPT-powered agent for Path of Exile 2 with up-to-date game data that helps players synergize their builds, assess their gear, search for valuable trades, create loot filters, answer game-related questions, and more.

![alt text](screenshots/lvl3_support_gems.png)

## Description

This GPT-powered agent analyzes PoE2 wiki data, popular PoE2 build webpages, current game data, and real-time player data to offer insights and recommendations. This agent is not intended to create builds for you but to aid you on your journey. 

## Planned Features

### Completed
- [X] **General Game Knowledge Assistance**  
  e.g., "How does Acrobatics work?"

- [X] **Build Optimization Suggestions**  
  e.g., "What are the meta builds right now?"

### In Progress / Upcoming
- [ ] **Gear Upgrade Assessment**  
  Upload a screenshot of an item and ask, "Is this an upgrade for me?"

- [ ] **Synergies Analysis**  
  e.g., "What skill gems work well with X?"

- [ ] **Tailored Loot Filter Generation**  
  e.g., "Make a basic early-game loot filter for my character that ignores grey items."

- [ ] **Trade Search**  
  e.g., "What are some good swords available on the market for my character?"

## Data Sources
- [x] [Official POE2 Wiki](https://www.poe2wiki.net/wiki/Path_of_Exile_2_Wiki)
- [x] Web searches (responsibly -- respects robots.txt and sitemaps)
- [ ] PoE 2 Game Data
- [ ] PoE 2 API (not yet available) - Trade data, non-authenticated player data
- [ ] YouTube Transcripts


None of the data mentioned above (except for game data) is stored or used for any other purposes. This data is requested by the user and is only accessible during the user's chat interface session.

## Prerequisites

- [OpenAI API key](https://platform.openai.com/settings/organization/api-keys)
- [Docker](https://www.docker.com/products/docker-desktop/)

## Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and add your OpenAI API key
    ```sh
    cp .env.example .env
    ```
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

## Login (for the short-term)
Email: admin

Password: admin

## Development Notes

This project uses:

- Poetry for dependency management
- Black for code formatting
- Ruff for linting
- MyPy for type checking
- Chainlit as an LLM framework with UI
- Playwright for rendered web scraping
- Fly.io for deployment

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Path of Exile 2 and all related content are property of Grinding Gear Games. Go Support them!
- Chainlit
