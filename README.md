# forward_messages_userbot

**1. Setup environment**

```cp .env.example .env```

1. API_ID and API_HASH you can get there [https://my.telegram.org/auth?to=apps](https://my.telegram.org/auth?to=apps)
2. Put your PHONE_NUMBER and any ACCOUNT_NAME
3. TELEGRAM_ID you can give it in  [@myidbot](https://t.me/myidbot)
   1. ADMIN_TELEGRAM_ID additional
4. You need to create bot with [@botfather](https://t.me/botfather) and put BOT_API
5. If you will run app with docker-compose yout DB_HOST equal postgress service name ("db" by default)

**2. Start docker stack**

```docker-compose up -d```