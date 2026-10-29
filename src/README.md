
# Hihg-load FastAPI service in a nutshell lab.

The project was made to learn Redis, Locust, RabbitMQ and high-load backend basics.

## Screenshots

Nothing here for now

## Stages
- [x] use '[]' and [x] to complete status

- [ ] Build simple backend architecture on FastAPI

- [ ] collect metrics with locast load test

- [ ] add Technologies

- [ ] collect metrics again and compare


## Metrics (before)

| Layer | Technologies |
|------|-----------|
| **Frontend** | aiogram |
| **Backend** | Python, SQLAlchemy, UV (package manager) |
| **DataBase** | PostgreSQL |

## Metrics (after)

| Layer | Technologies |
|------|-----------|
| **Frontend** | aiogram |
| **Backend** | Python, SQLAlchemy, UV (package manager) |
| **DataBase** | PostgreSQL |


## Conclusion

...

## 📂 Project Structure

```text
├── src/
│   ├── database/    # SQLAlchemy table models and database logic
│   ├── handlers/    # aiogram handlers for bot commands
│   ├── parse/       # Data parsing and cleaning
│   ├── services/    # Business logic
│   ├── utils/       # Helper utilities (monitoring, logging)
│   ├── main.py      # Bot entry point
│   ├── keyboards.py # Reply keyboards for the bot
│   ├── process.py   # Main process where everything starts
│   └── config.py    # Configuration file
├── pyproject.toml   # Dependencies and configuration (uv, ruff, pyright)
└── README.md
```

## Environment Variables

To run this project, you need copy .env.example [ADD here how]

## Run with Docker

```bash
docker compose up -d
```

## Run Locally

...

## 👤 Author

- GitHub: <https://github.com/Zeufo>
- Telegram: @Zeufo

## License

[MIT](https://choosealicense.com/licenses/mit/)
