FROM python:3.8.2-alpine3.11

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY discord_bot.py /

EXPOSE 9481
ENTRYPOINT [ "python3", "/discord_bot.py" ]