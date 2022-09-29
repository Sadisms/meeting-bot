# Meeting-Bot

### Установка 

```shell
copy .env_meeting.example .env_meeting
python -m venv .venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r custom_reqs.txt
python .\migrator.py migrate
```
Заполнить .env_meeting.
Cкопировать credls OAUTH google в token.json

### Авторизация Slack
```shell
python .\auth.py
```
В контейнере:
```shell
docker-compose up -d auth
```
Далее появится файл etc/auth в нём будет ссылка на ngrok. 
Ссылку указываем в настройках бота в разделе OAuth


### Запуск бота

```shell
python .\app.py
python .\oauth_server.py
ngrok http 5000 # Адрес занести в .env
```

### Запуск в контейнере
```shell
docker-compose build --no-cache bot
docker-compose run bot python3 migrator.py migrate
docker-compose up -d oauth-server
docker-compose up -d bot
```

### Авторизация в Google
В папке etc после запуска oauth-server'a появится файл(с url ngrok'a на сервер) с одноименным названием, 
данный URl нужно указать в:
```shell
google console > Credentials > OAuth 2.0 Client IDs
Authorized JavaScript origins(сама URL) и Authorized redirect URIs(url + /oauth2callback)
```