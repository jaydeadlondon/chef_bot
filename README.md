# Chief — Your AI Chef on Telegram

Chief is an intelligent dinner planning assistant powered by the GigaChat neural network. The bot helps transform the ingredients in your fridge into complete recipes, taking into account your dietary preferences, allergies, and the number of guests.

## ✨ Key Features

- Smart recipe selection: generates step-by-step instructions based on your ingredient list.
- Personalization (Profile): Enter your allergies or preferences (vegan, healthy eating, lactose-free) once, and the bot will take them into account with every request.
- Nutrition Calculator: automatically estimates calories, protein, fat, and carbohydrates for each dish.
- Cookbook (Favorites): saves your favorite recipes in a PostgreSQL database for quick access.
- Shopping List: instantly generates a list of ingredients from a recipe for your next trip to the store.
- Built-in timers: receive ready notifications right within the chat.
- Security: integrated content filter (protection against incorrect or inedible requests).

## 🛠 Technology Stack

- Language: Python 3.10+
- Bot platform: aiogram 3.x (asyncio)
- Neural network (LLM): GigaChat API (SberDevices)
- Database: PostgreSQL 15
- ORM: SQLAlchemy 2.0 (asyncpg asynchronous driver)
- FSM & Cache: Redis (user state storage)
- Containerization: Docker & Docker Compose
- Data validation: Pydantic Settings 2.x

## 🚀 Quick Start

### 1. Setting up the environment

   Make sure you have Docker and Docker Compose installed.

### 2. Cloning the repository

```bash
git clone https://github.com/jaydeadlondon/chef_bot.git
cd chef_bot
```

### 3. Configuring environment variables

Create a `.env` file in the project root directory and specify the required variables:

```env
# Telegram
BOT_TOKEN=your_bot_father_token

# AI (GigaChat)
GIGACHAT_CREDENTIALS=your_gigachat_api_key

# PostgreSQL
POSTGRES_USER=chef_user
POSTGRES_PASSWORD=chef_password
POSTGRES_DB=chef_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### 4. Running via Docker

```bash
docker-compose up --build -d
```

The bot will automatically apply the database schema and start running. 

## 📁 Project Structure

```text
chef_bot/
├── core/               # Pydantic configuration and settings
├── database/           # SQLAlchemy models, engine, and repositories
├── handlers/           # Command and message processing logic (Common, Recipes, Profile)
├── middlewares/        # Dependency injection (DB Session)
├── services/           # Integration with external APIs (GigaChat Service)
├── states/             # FSM state definitions
├── Dockerfile          # Instructions for building the application image
├── docker-compose.yml  # Container orchestration (App, DB, Redis)
├── main.py             # Application entry point
└── requirements.txt    # Project dependencies
```

## 🏗 Architectural Principles

The project adheres to the SOLID principles:

- Single Responsibility: each handler and service is responsible only for its own task.
- Dependency Inversion: interaction with the neural network is hidden behind the `AIService` abstraction, allowing the model to be replaced (with ChatGPT/YandexGPT) without changing the business logic.
- Repository Pattern: database operations are isolated from the Telegram bot’s logic.

## 📝 Bot Commands

- `/start` — Restart and return to the main menu.
- `/my_recipes` — View saved recipes.
- `/profile` — Set dietary preferences.
