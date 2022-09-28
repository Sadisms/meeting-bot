# Meeting-Bot

### Установка 

```shell
copy .env.example .env
# Заполнить .env
python -m venv .venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r custom_reqs.txt
python .\migrator.py migrate
# Скопировать credls OAUTH google в token.json
```

### Запуск бота

```shell
python .\app.py
python .\oauth_server.py
ngrok http 5000 # Адрес занести в .env
```

### Запуск в контейнере
```shell
docker-compose build --no-cache meeting-bot
docker-compose run meeting-bot python3 migrator.py migrate
docker-compose up -d
```