# Lamoda and Twitch parsers
Backend on FastAPI with BeautifulSoup, MongoDB and Kafka.

## Instalation
1. Clone the repository:

```
$ git clone git@github.com:may42day/parser-twitch-lamoda.git
$ cd parser-twitch-lamoda
```
2. Fill in .env file or use .env_example:
```
$ mv .env_example .env
```

3. Build docker containers:
```
$ docker-compose up -d
```

4. Application started. Navigate to http://127.0.0.1:8000

