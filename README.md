# UniRoadMap EUC Testing

[Открыть бота в Telegram](http://t.me/urm_eucti_bot)

## Инструкции по запуску бота
#### Параметры бота (.env)
```.env
# Bot
API_TOKEN=сюда свой токен для бота
ADMINS_IDS=[здесь нужно перечислить id админов через запятую без ковычек]

# Postgres
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis
POSTGRES_DB=app
```
#### Подготовка БД
```shell script
docker-compose run bot bash /app/migrate.sh
```
#### Запуск бота
**Для продакшена**
```shell script
docker-compose -f docker-compose.yml up -d
```
**Для разработки**
```shell script
docker-compose up
```
## Internationalization
#### Поиск текстов для перевода в файлах бота
```shell script
pybabel extract . -o locales/bot.pot
```

#### Подготовка найденных текстов к переводу
**Внимание эта команда перезаписывает все переводы которые были до этого!**
```shell script
echo {en,ru} | xargs -n1 pybabel init -i locales/bot.pot -d locales -D bot -l
```

#### Компиляция переводов
```shell script
pybabel compile -d locales -D bot
```