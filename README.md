# Discord Bot for Telegram
## Introduction
This is very very simple bot for telegram and alertmanager.
We have an issue about network connectivity, so we develope a simple app to send prometheus alertmanager alerts to discord.
This script in development... if you can or you want, help us to finish it. Thanks.

## Requirements
It depends on just `requests`. And you need webhook address of `discord`.

### Discord Webhook
1. When you Discord opened, you can create channel or use general channel. Click on `Edit Channel`
    ![Edit Channel](https://github.com/sinamoghaddas/discord_bot/raw/master/image/discord-webhook-1.png "Edit Channel")
2. Click on `Webhooks`
    ![Webhooks](https://github.com/sinamoghaddas/discord_bot/raw/master/image/discord-webhook-2.png "Webhooks")
3. Click on `Create Webhook`
    ![Create webhook](https://github.com/sinamoghaddas/discord_bot/raw/master/image/discord-webhook-3.png "Create webhook")
4. Write a name for your webhook, you can upload image, Click on `Copy` in front of webhook address, then click on `Save` to finish
    ![Create webhook](https://github.com/sinamoghaddas/discord_bot/raw/master/image/discord-webhook-4.png "Create webhook")
5. Now you have your webhook url and you can use it apps

## Usage
### Docker
```bash
docker run \
    --name discord_not \
    -it \
    -p 127.0.0.1:9481:9481 \
    -e URL='YOUR-WEBHOOK-ADDRESS' \
    moghaddas/discord_bot:latest
```

### Simple
```bash
git clone https://github.com/sinamoghaddas/discord_bot
cd discord_bot

pip install -r requirements.txt

./discord_bot.py -h                                                                                                                                                                               :(
usage: discord_bot.py [-h] -U URL [-H HOST] [-p PORT] [-u USER]

optional arguments:
  -h, --help            show this help message and exit
  -U URL, --url URL     webhook url
  -H HOST, --host HOST  listen address (default 0.0.0.0)
  -p PORT, --port PORT  listen port (default 9481)
  -u USER, --user USER  user in discord




./discord_bot.py -U <YOUR-WEBHOOK-ADDRESS>

```
