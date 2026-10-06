# 📈 TickerTracker Bot

An automated, containerized service and Telegram bot for tracking real-time prices of financial assets (stocks, currencies, cryptocurrencies) using **Django 6.0**, **aiogram 3.x**, **yfinance**, and **Celery/Redis**.

---

## 🚀 Key Features

- 🤖 **Telegram Bot (aiogram 3.x):**
  - Step-by-step alert creation using Finite State Machine (FSM).
  - Interactive menu with Reply and Inline keyboards.
  - View active alerts (`/myalerts`) with native currency symbols (USD, EUR, GBP, UAH, etc.).
  - One-click alert deletion directly from the Telegram chat.
- 📊 **Price Tracking & Data Integration:**
  - Real-time market data extraction powered by `yfinance`.
  - Multi-currency support with custom currency symbol mapping.
- ⚡ **Background Tasks & Notifications (Celery + Redis):**
  - Periodic background checks for target price thresholds.
  - Instant Telegram notifications sent upon price alert triggers.
- 🔌 **REST API (Django REST Framework):**
  - Endpoints to manage tickers, fetch historical price data, and control user alerts.
- 🐳 **Full Containerization (Docker & Docker Compose):**
  - Isolated environment for Web, Bot, Celery worker/beat, Redis, and PostgreSQL.

---

## 🛠 Tech Stack

- **Language:** Python 3.13
- **Backend Framework:** Django 6.0, Django REST Framework
- **Telegram Bot Engine:** aiogram 3.x
- **Database:** PostgreSQL 15
- **Task Queue & Broker:** Celery + Redis
- **Data Source:** `yfinance`
- **Testing:** pytest, pytest-django, unittest.mock
- **Containerization:** Docker, Docker Compose

---

## 🏗 Project Architecture

```text
TickerTracker/
├── alerts/              # Django app for managing price alerts (models, API)
├── trackers/            # Django app for tickers, price history, and Celery tasks
├── config/              # Django project settings, URLs, and Celery config
├── bot.py               # Main entry point for the Telegram bot (aiogram)
├── docker-compose.yml   # Docker services configuration
├── Dockerfile           # Python environment build instructions
├── requirements.txt     # Python project dependencies
└── tests/               # Unit and integration test suite (pytest)
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/DariaNott/TickerTracker.git
cd TickerTracker
```

### 2. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory and add the following variables:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web

# PostgreSQL
POSTGRES_DB=tickertracker_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis & Celery
REDIS_URL=redis://redis:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
```

### 3. Run with Docker Compose
Start all containers (DB, Redis, Django Web, Celery Worker, Celery Beat, and Bot) in background mode:

```bash
docker compose up -d --build
```

### 4. Apply Migrations & Create Superuser
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## 🧪 Running Tests

The project includes unit and integration coverage for REST API endpoints, Celery tasks, models, and Telegram notification services using `pytest`.

To run the complete test suite inside the container:

```powershell
docker compose exec web pytest
```

---

## 📱 Telegram Bot Commands

<table>
  <thead>
    <tr>
      <th scope="col">Command</th>
      <th scope="col">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>/start</code></td>
      <td>Initialize the bot and display the main menu.</td>
    </tr>
    <tr>
      <td><code>/newalert</code></td>
      <td>Launch the step-by-step FSM wizard to create a new price alert.</td>
    </tr>
    <tr>
      <td><code>/myalerts</code></td>
      <td>Display active alerts with options to delete them via inline buttons.</td>
    </tr>
  </tbody>
</table>