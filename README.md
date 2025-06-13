# Telegram to Gofile Shortlink Bot 🤖

This bot:
- Watches a source channel for media.
- Uploads to Gofile.io.
- Shortens the link via API.
- Posts to target channel with thumbnail.

## 🌍 Env Variables

- BOT_TOKEN
- SHORTLINK_API
- SHORTLINK_URL (optional)
- PORT (for Koyeb, default: 8080)

## 🚀 Deploy with Docker

```bash
docker build -t tg-gofile-bot .
docker run -e BOT_TOKEN=xxx -e SHORTLINK_API=https://short.site/api?url= tg-gofile-bot
