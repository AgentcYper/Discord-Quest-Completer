# Soar Team - Discord Quest Solver

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Discord-API-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" />
  <img src="https://img.shields.io/badge/Windows-Supported-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/Linux-Supported-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux" />
  <img src="https://img.shields.io/badge/macOS-Supported-000000?style=for-the-badge&logo=apple&logoColor=white" alt="macOS" />
</p>

A fast and lightweight Python CLI tool designed to automatically solve Discord Quests without having to download or run games

---

## Features

- Supports all major quest task types
  - `PLAY_ON_DESKTOP`
  - `STREAM_ON_DESKTOP`
  - `WATCH_VIDEO`
  - `WATCH_VIDEO_ON_MOBILE`
  - `PLAY_ACTIVITY`
- Automatically retrieves active quests directly from Discord API
- Batch solve all quests or single quest selection
- Dark blue and white terminal interface with real time progress bars
- Clean pagination system with five quests per page
- Token switcher to manage multiple accounts easily

---

## Prerequisites

- Python 3.8 or newer
- Windows or Linux or macOS

---

## Installation

Clone the repository and install requirements

```bash
git clone https://github.com/AgentcYper/Discord-Quest-Completer.git
cd Discord-Quest-Completer
pip install -r requirements.txt
```

---

## Usage

Run the tool using the batch script or directly via python

```bash
run.bat
```

Or

```bash
python main.py
```

### Steps

1. Enter your Discord account token when prompted
2. Choose a quest number to solve or type `all` to solve everything

---

## Available Commands

- `1` - `5`: Solve specific quest from current page
- `all`: Solve all remaining quests sequentially
- `next` / `prev`: Navigate between pages
- `token`: Change active account token
- `r`: Refresh quests list
- `cls`: Clear terminal screen
- `exit`: Exit the tool

---

## Developers

<p align="center">
  <a href="https://github.com/AgentcYper">
    <img src="https://img.shields.io/badge/AgentcYper-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="AgentcYper" />
  </a>
  <a href="https://github.com/nf5054">
    <img src="https://img.shields.io/badge/nf5054-GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="nf5054" />
  </a>
</p>

---

## Disclaimer

This software is for educational and research purposes only
Automating user accounts violates Discord Terms of Service
Use entirely at your own risk
